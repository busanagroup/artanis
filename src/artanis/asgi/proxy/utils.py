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
import ipaddress
import logging
import warnings
from functools import lru_cache
from textwrap import dedent
from typing import Protocol, TypeVar, Union, Any, TypedDict, Optional, Mapping, Iterable

import httpx
from starlette import status
from starlette.background import BackgroundTask
from starlette.datastructures import Headers, MutableHeaders
from starlette.responses import JSONResponse
from starlette.types import Scope
from typing_extensions import deprecated, overload

from artanis.asgi.proxy.base import ConnectionHeaderParseResult
from artanis.asgi.proxy.exceptions import BaseURLError, UnsupportedHttpVersionError

logger = logging.getLogger(__name__)

ProxyFilterTypeVar = TypeVar("ProxyFilterTypeVar", bound="ProxyFilterProto")


class ProxyFilterProto(Protocol):
    """All proxy filter must implement like this."""

    def __call__(self, url: httpx.URL, /) -> Union[None, str]: ...


class LoggerProtocol(Protocol):
    """Like logging.error() ."""

    def __call__(
            self,
            *,
            msg: object,
            exc_info: Union[BaseException, None, bool],
    ) -> Any: ...


class ErrMsg(TypedDict):
    """A error message of response.

    Attributes:
        err_type: equal to {type(error).__name__}.
        msg: equal to {str(error)}.
    """

    # NOTE: `err_type` 和 `msg` 键是api设计的一部分
    err_type: str
    msg: str


class ErrResponseJson(TypedDict):
    """A json-like dict for return by `JSONResponse`.

    Something like:
    ```json
    {
        "detail": {
            "err_type": "RuntimeError",
            "msg": "Something wrong."
        }
    }
    ```
    """

    # https://fastapi.tiangolo.com/tutorial/handling-errors/#httpexception
    detail: ErrMsg


@deprecated(
    "May or may not be removed in the future.", category=PendingDeprecationWarning
)
def reset_lru_get_url(
        maxsize: Union[int, None] = 128,
        typed: bool = False
) -> None:
    """Reset the parameters or clear the cache of `lru_get_url`.

    Args:
        maxsize: The same as `functools.lru_cache`.
        typed: The same as `functools.lru_cache`.
    """
    global _lru_get_url
    _lru_get_url.cache_clear()
    _lru_get_url = lru_cache(maxsize, typed)(_lru_get_url.__wrapped__)


@deprecated(
    "May or may not be removed in the future.", category=PendingDeprecationWarning
)
@lru_cache(maxsize=1024)
def _lru_get_url(url: str) -> httpx.URL:
    return httpx.URL(url)


@deprecated(
    "May or may not be removed in the future.", category=PendingDeprecationWarning
)
def lru_get_url(url: str) -> httpx.URL:
    """Lru cache for httpx.URL(url)."""
    return _lru_get_url(url).copy_with()


def check_base_url(base_url: Union[httpx.URL, str], /) -> httpx.URL:
    """Check and format base_url.

    - Time consumption: 56.2 µs ± 682 ns.

    Args:
        base_url: url that need to be checked and formatted.
            - If base_url is a str, it will be converted to httpx.URL.

    Raises:
        BaseURLError:
            - if base_url does not contain {scheme} or {netloc}.
            - if base_url does not ends with "/".

    Returns:
        `base_url.copy_with(query=None, fragment=None)`
            - The copy of original `base_url`.

    Examples:
        r = check_base_url("https://www.example.com/p0/p1?q=1")
        assert r == "https://www.example.com/p0/"

    The components of a URL are broken down like this:
        https://jo%40email.com:a%20secret@müller.de:1234/pa%20th?search=ab#anchorlink
        [scheme]   [  username  ] [password] [ host ][port][ path ] [ query ] [fragment]
                [       userinfo        ] [   netloc   ][    raw_path    ]
    """
    example_url = "https://www.example.com/path/"

    base_url = (
        base_url.copy_with() if isinstance(base_url, httpx.URL) else httpx.URL(base_url)
    )

    if not base_url.scheme or not base_url.netloc:
        raise BaseURLError(
            dedent(
                f"""\
                `base_url` must contain scheme and netloc,
                e.g. {example_url}
                got: {base_url}\
                """
            )
        )

    if base_url.query or base_url.fragment:
        base_url = base_url.copy_with(query=None, fragment=None)
        warnings.warn(
            dedent(
                f"""\
                `base_url` should not contain `query` or `fragment`, which will be ignored.
                The `base_url` will be treated as: {base_url}\
                """
            ),
            stacklevel=2,
        )

    if not str(base_url).endswith("/"):
        msg = dedent(
            f"""\
            `base_url` must ends with "/", may be you mean:
            {base_url}/\
            """
        )
        raise BaseURLError(msg)

    return base_url


# TODO: https://fastapi.tiangolo.com/tutorial/handling-errors/
def return_err_msg_response(
        err: Union[BaseException, ErrMsg],
        /,
        *,
        # JSONResponse
        status_code: int,
        headers: Optional[Mapping[str, str]] = None,
        background: Optional[BackgroundTask] = None,
        # logger
        logger: Optional[LoggerProtocol] = None,
        _msg: Optional[Any] = None,
        _exc_info: Optional[BaseException] = None,
) -> JSONResponse:
    """Return a JSONResponse with error message and log the error message by logger.

    - logger(msg=_msg, exc_info=_exc_info)
    - JSONResponse(
        ...,
        status_code=status_code,
        headers=headers,
        background=background,
    )

    The error message like:
    ```json
    {
        "detail": {
            "err_type": "RuntimeError",
            "msg": "Something wrong."
        }
    }
    ```

    Args:
        err:
            If err is subclass of `BaseException`, it will be converted to `ErrMsg`.
            If err is a `ErrMsg`, it will be used directly.

        status_code: The status code of response.
        headers: The header of response. Defaults to None.
        background: The background task of response. Defaults to None.

        logger: Something like `logging.error`. Defaults to None.
            If it is None, will do nothing.
            If it is not None, it will be used to log error message.
        _msg: The msg to log. Defaults to None.
            If it is None, it will be set to `JSONResponse` content.
        _exc_info: The detailed error info to log. Defaults to None.
            If it is None, will do nothing.
            If it is not None, will be passed to logger.

    Raises:
        TypeError: If err is not a BaseException or ErrMsg.

    Returns:
        JSONResponse about error message.
    """
    if isinstance(err, BaseException):
        detail = ErrMsg(err_type=type(err).__name__, msg=str(err))
    else:
        detail = err

    err_response_json = ErrResponseJson(detail=detail)

    if logger is not None:
        logger(
            msg=(
                _msg if _msg is not None else err_response_json
            ),
            exc_info=_exc_info,
        )
    else:
        if _msg is not None or _exc_info is not None:
            warnings.warn(
                "You should pass logger to record error message, "
                "or you can ignore this warning if you don't want to record error message.",
                stacklevel=2,
            )

    return JSONResponse(
        content=err_response_json,
        status_code=status_code,
        headers=headers,
        background=background,
    )


def check_http_version(
        scope: Scope,
        supported_versions: Iterable[str]
) -> Union[JSONResponse, None]:
    """Check whether the http version of scope is in supported_versions.

    Args:
        scope: asgi scope dict.
        supported_versions: The supported http versions.

    Returns:
        If the http version of scope is not in supported_versions, return a JSONResponse with status_code=505,
        else return None.
    """
    # https://asgi.readthedocs.io/en/latest/specs/www.html#http-connection-scope
    # https://asgi.readthedocs.io/en/latest/specs/www.html#websocket-connection-scope
    http_version: str = scope.get("http_version", "")
    if http_version not in supported_versions and http_version != "":
        error = UnsupportedHttpVersionError(
            f"The request http version is {http_version}, but we only support {supported_versions}."
        )
        return return_err_msg_response(
            error,
            status_code=status.HTTP_505_HTTP_VERSION_NOT_SUPPORTED,
            logger=logger.info,
        )


def default_proxy_filter(url: httpx.URL) -> Union[None, str]:
    """Filter by host.

    Reject the following hosts:

    - if the host is ip address, and is not global ip address. e.g:
        - `http://127.0.0.1`
        - `http://192.168.0.1`
    - if the host contains "localhost".

    Warning:
        It will consumption time: 3.22~4.7 µs ± 42.6 ns.

    Args:
        url: The target url of the client request to proxy.

    Returns:
        None: should accept the proxy request.
        str: should rejetc the proxy request.
            The `str` is the reason of reject.
    """
    host = url.host
    if "localhost" in host:
        return "Deny proxy for localhost."

    try:
        ip_address = ipaddress.ip_address(host)
    except ValueError:
        return None

    if not ip_address.is_global:
        return "Deny proxy for non-public IP addresses."

    return None


@overload
def warn_for_none_filter(proxy_filter: ProxyFilterTypeVar) -> ProxyFilterTypeVar: ...


@overload
def warn_for_none_filter(proxy_filter: None) -> ProxyFilterProto: ...


def warn_for_none_filter(proxy_filter: ProxyFilterProto) -> ProxyFilterProto:
    """Check whether the argument `proxy_filter` is None.

    Args:
        proxy_filter: The argument need to be check.

    Returns:
        If proxy_filter is None, will warn user and return `default_proxy_filter`.
    Else will just return the original argument `proxy_filter`.
    """
    if proxy_filter is None:
        msg = dedent(
            """\
            The `proxy_filter` is None, which means no filter will be used.
            It is not recommended, because it may cause security issues.

            A default proxy filter will be used, which will reject the proxy request:
             - if the host of url is ip address, and is not global ip address.
            """
        )
        warnings.warn(msg, stacklevel=3)
        return default_proxy_filter
    else:
        return proxy_filter


def change_necessary_client_header_for_httpx(
        *, headers: Headers, target_url: httpx.URL
) -> MutableHeaders:
    """Change client request headers for sending to proxy server.

    - Change "host" header to `target_url.netloc.decode("ascii")`.
    - If "Cookie" header is not in headers,
        will forcibly add a empty "Cookie" header
        to avoid httpx.AsyncClient automatically add another user cookiejar.

    Args:
        headers: original client request headers.
        target_url: httpx.URL of target server url.

    Returns:
        New requests headers, the copy of original input headers.
    """
    # https://www.starlette.io/requests/#headers
    new_headers = headers.mutablecopy()

    new_headers["host"] = target_url.netloc.decode("ascii")

    # https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers/Cookie

    # FIX: https://github.com/WSH032/fastapi-proxy-lib/security/advisories/GHSA-7vwr-g6pm-9hc8
    # forcibly set `Cookie` header to avoid httpx.AsyncClient automatically add another user cookiejar
    if "Cookie" not in new_headers:  # case-insensitive
        new_headers["Cookie"] = ""

    return new_headers


def change_client_header(
        *,
        headers: Headers,
        target_url: httpx.URL
) -> ConnectionHeaderParseResult:
    new_headers = change_necessary_client_header_for_httpx(
        headers=headers, target_url=target_url
    )

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Connection#syntax
    client_connection_header = [
        v.strip() for v in new_headers.get("connection", "").lower().split(",")
    ]

    if "close" in client_connection_header:
        whether_require_close = True
        client_connection_header.remove("close")
    else:
        whether_require_close = False
    if "keep-alive" not in client_connection_header:
        client_connection_header.insert(0, "keep-alive")
    new_headers["connection"] = ",".join(client_connection_header)

    if "keep-alive" in new_headers:
        del new_headers["keep-alive"]

    return ConnectionHeaderParseResult(whether_require_close, new_headers)


def change_server_header(
        *,
        headers: httpx.Headers,
        require_close: bool
) -> httpx.Headers:
    """Change server response headers for sending to client.

    - If require_close is True, will make sure "connection: close" in headers, else will remove it.
    - And remove "keep-alive" header.

    Args:
        headers: server response headers
        require_close: whether require close connection

    Returns:
        The **oringinal headers**, but **had been changed**.
    """
    server_connection_header: list[str] = [
        v.strip() for v in headers.get("connection", "").lower().split(",")
    ]

    if require_close:
        if "close" not in server_connection_header:
            server_connection_header.insert(0, "close")
    else:
        if "close" in server_connection_header:
            server_connection_header.remove("close")

    if server_connection_header:
        headers["connection"] = ",".join(server_connection_header)
    else:
        if "connection" in headers:
            del headers["connection"]

    if "keep-alive" in headers:
        del headers["keep-alive"]

    return headers
