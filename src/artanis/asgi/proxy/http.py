#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Busana Apparel Group. All rights reserved.
#
# This product and it's source code is protected by patents, copyright laws and
# international copyright treaties, as well as other intellectual property
# laws and treaties. The product is licensed, not sold.
#
# The source code and sample programs in this package or parts hereof
# as well as the documentation shall not be copied, modified or redistributed
# without permission, explicit or implied, of the author.
#
# This module is part of Artanis Enterprise Platform and is released under
# the Apache-2.0 License: https://www.apache.org/licenses/LICENSE-2.0
import logging
from textwrap import dedent
from typing import Optional, Union, Any, NoReturn

import httpx
from starlette import status
from starlette.background import BackgroundTasks
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from typing_extensions import override

from artanis.asgi.proxy.base import BaseProxy
from artanis.asgi.proxy.exceptions import ReverseProxyServerError, RejectedProxyRequestError, BadTargetUrlError
from artanis.asgi.proxy.utils import ProxyFilterProto, check_http_version, change_client_header, change_server_header, \
    check_base_url, return_err_msg_response, warn_for_none_filter

logger = logging.getLogger(__name__)

# https://developer.mozilla.org/docs/Web/HTTP/Methods
_NON_REQUEST_BODY_METHODS = ("GET", "HEAD", "OPTIONS", "TRACE")
"""The http methods that should not contain request body."""

# https://asgi.readthedocs.io/en/latest/specs/www.html#http-connection-scope
SUPPORTED_HTTP_VERSIONS = ("1.0", "1.1")
"""The http versions that we supported now. It depends on `httpx`."""

# https://www.python-httpx.org/exceptions/
_400_ERROR_NEED_TO_BE_CATCHED_IN_FORWARD_PROXY = (
    httpx.InvalidURL,
    httpx.UnsupportedProtocol,
    httpx.ProtocolError,
)
"""These errors need to be caught.
When:
- client.build_request
- client.send
"""
_500_ERROR_NEED_TO_BE_CATCHED_IN_FORWARD_PROXY = (
    httpx.ConnectError,
)
"""These errors need to be caught and return 5xx status_code.
When:
- client.build_request
- client.send
"""

_502_ERROR_NEED_TO_BE_CATCHED_IN_REVERSE_PROXY = (
    httpx.TransportError,
    httpx.InvalidURL,
    httpx.StreamError,
)
"""When these errors occur in reverse proxy server, we think it is error of server."""


class BaseHttpProxy(BaseProxy):
    """Http proxy base class.

    Attributes:
        client: The `httpx.AsyncClient` to send http requests.
        follow_redirects: Whether follow redirects of target server.
    """

    @override
    async def send_request_to_target(  # pyright: ignore [reportIncompatibleMethodOverride]
            self, *, request: Request, target_url: httpx.URL
    ) -> Response:
        """Change request headers and send request to target url.

        - The http version of request must be in [`SUPPORTED_HTTP_VERSIONS`][fastapi_proxy_lib.core.http.SUPPORTED_HTTP_VERSIONS].

        Args:
            request: the original client request.
            target_url: target url that request will be sent to.

        Returns:
            The response from target url.
        """
        client = self.client
        follow_redirects = self.follow_redirects

        check_result = check_http_version(request.scope, SUPPORTED_HTTP_VERSIONS)
        if check_result is not None:
            return check_result

        require_close, proxy_header = change_client_header(
            headers=request.headers, target_url=target_url
        )

        request_content = (
            None if request.method in _NON_REQUEST_BODY_METHODS else request.stream()
        )

        client.cookies.clear()

        proxy_request = client.build_request(
            method=request.method,
            url=target_url,
            params=tuple(request.query_params.multi_items()),
            headers=proxy_header,
            content=request_content,
        )

        logger.debug(
            "HTTP: client:%s ; url:%s ; head:%s",
            request.client,
            proxy_request.url,
            proxy_request.headers,
        )

        proxy_response = await client.send(
            proxy_request,
            stream=True,
            follow_redirects=follow_redirects,
        )

        tasks = BackgroundTasks()
        tasks.add_task(proxy_response.aclose)

        proxy_response_headers = change_server_header(
            headers=proxy_response.headers, require_close=require_close
        )
        return StreamingResponse(
            content=proxy_response.aiter_raw(),
            status_code=proxy_response.status_code,
            headers=proxy_response_headers,
            background=tasks,
        )

    @override
    async def proxy(self,
                    *args,
                    **kwargs
                    ) -> NoReturn:
        """NotImplemented."""
        raise NotImplementedError()


class ReverseHttpProxy(BaseHttpProxy):
    """Reverse http proxy."""

    client: httpx.AsyncClient
    follow_redirects: bool
    base_url: httpx.URL

    @override
    def __init__(
            self,
            client: Optional[httpx.AsyncClient] = None,
            *,
            base_url: Union[httpx.URL, str],
            follow_redirects: bool = False,
    ) -> None:
        """Reverse http proxy.

        Note: please make sure `base_url` is available.
            Because when an error occurs,
            we cannot distinguish whether it is a proxy server network error, or it is a error of `base_url`.
            So, we will return 502 status_code whatever the error is.

        Args:
            client: The `httpx.AsyncClient` to send http requests. Defaults to None.<br>
                If None, will create a new `httpx.AsyncClient`,
                else will use the given `httpx.AsyncClient`.
            follow_redirects: Whether follow redirects of target server. Defaults to False.
            base_url: The target proxy server url.
        """
        self.base_url = check_base_url(base_url)
        super().__init__(client, follow_redirects=follow_redirects)

    @override
    async def proxy(
            self,
            *,
            request: Request,
            path: Optional[str] = None
    ) -> Response:
        """Send request to target server.

        Args:
            request: `starlette.requests.Request`
            path: The path params of request, which means the path params of base url.<br>
                If None, will get it from `request.path_params`.<br>
                **Usually, you don't need to pass this argument**.

        Returns:
            The response from target server.
        """
        base_url = self.base_url

        path_param: str = (
            path if path is not None else next(iter(request.path_params.values()), "")
        )

        target_url = base_url.copy_with(
            path=(base_url.path + path_param)
        )  # 耗时: 18.4 µs ± 262 ns

        try:
            return await self.send_request_to_target(
                request=request, target_url=target_url
            )
        except _502_ERROR_NEED_TO_BE_CATCHED_IN_REVERSE_PROXY as e:
            msg = dedent(
                f"""\
                Error in ReverseHttpProxy().proxy():
                url: {target_url}
                request headers: {request.headers}
                """
            )

            return return_err_msg_response(
                ReverseProxyServerError(
                    "Something wrong! Please contact the server maintainer!"
                ),
                status_code=status.HTTP_502_BAD_GATEWAY,
                logger=logger.exception,
                _msg=msg,
                _exc_info=e,
            )


class ForwardHttpProxy(BaseHttpProxy):
    """Forward http proxy."""

    client: httpx.AsyncClient
    follow_redirects: bool
    proxy_filter: ProxyFilterProto

    @override
    def __init__(
            self,
            client: Optional[httpx.AsyncClient] = None,
            *,
            follow_redirects: bool = False,
            proxy_filter: ProxyFilterProto | None = None,
    ) -> None:
        """Forward http proxy.

        Args:
            client: The `httpx.AsyncClient` to send http requests. Defaults to None.<br>
                If None, will create a new `httpx.AsyncClient`,
                else will use the given `httpx.AsyncClient`.
            follow_redirects: Whether follow redirects of target server. Defaults to False.
            proxy_filter: Callable Filter, decide whether reject the proxy requests.
                If None, will use the default filter.
        """
        self.proxy_filter = warn_for_none_filter(proxy_filter)
        super().__init__(client, follow_redirects=follow_redirects)

    @override
    async def proxy(
            self,
            *,
            request: Request,
            path: Optional[str] = None,
    ) -> Response:
        """Send request to target server.

        Args:
            request: `starlette.requests.Request`
            path: The path params of request, which means the full url of target server.<br>
                If None, will get it from `request.path_params`.<br>
                **Usually, you don't need to pass this argument**.

        Returns:
            The response from target server.
        """
        proxy_filter = self.proxy_filter

        path_param: str = (
            next(iter(request.path_params.values()), "") if path is None else path
        )
        if path_param == "":
            error = BadTargetUrlError("Must provide target url.")
            return return_err_msg_response(
                error, status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            target_url = httpx.URL(path_param)
        except httpx.InvalidURL as e:  # pragma: no cover
            return return_err_msg_response(
                e,
                status_code=status.HTTP_400_BAD_REQUEST,
                logger=logger.critical,
            )

        filter_result = proxy_filter(target_url)
        if filter_result is not None:
            return return_err_msg_response(
                RejectedProxyRequestError(filter_result),
                status_code=status.HTTP_403_FORBIDDEN,
            )

        try:
            return await self.send_request_to_target(
                request=request, target_url=target_url
            )
        except _400_ERROR_NEED_TO_BE_CATCHED_IN_FORWARD_PROXY as e:
            return return_err_msg_response(
                e, status_code=status.HTTP_400_BAD_REQUEST
            )
        except _500_ERROR_NEED_TO_BE_CATCHED_IN_FORWARD_PROXY as e:
            return return_err_msg_response(
                e,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                logger=logger.exception,
                _exc_info=e,
            )
