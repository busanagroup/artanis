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
import typing as t

from artanis import concurrency
from artanis.asgi import http, types
from artanis.asgi.endpoints.base import BaseEndpoint

if t.TYPE_CHECKING:
    from artanis.asgi.asgibase import BaseASGIService

__all__ = ["HTTPEndpoint"]


class HTTPEndpoint(BaseEndpoint, types.HTTPEndpointProtocol):
    def __init__(self, scope: "types.Scope", receive: "types.Receive", send: "types.Send") -> None:
        """An HTTP endpoint.

        :param scope: ASGI scope.
        :param receive: ASGI receive function.
        :param send: ASGI send function.
        """
        if scope["type"] != "http":
            raise ValueError("Wrong scope")

        super().__init__(scope, receive, send)

        self.state.update(
            {
                "request": http.Request(scope, receive=receive),
            }
        )

    @classmethod
    def allowed_methods(cls) -> set[str]:
        """The list of allowed methods by this endpoint.

        :return: List of allowed methods.
        """
        methods = {
            method for method in http.Method.__members__.keys() if getattr(cls, method.lower(), None) is not None
        }
        if "GET" in methods:
            methods.add("HEAD")
        return methods

    @classmethod
    def allowed_handlers(cls) -> dict[str, t.Callable]:
        """A mapping of handler related to each HTTP method.

        :return: Handlers mapping.
        """
        return {method: getattr(cls, method.lower(), getattr(cls, "get")) for method in cls.allowed_methods()}

    @property
    def handler(self) -> t.Callable:
        """The handler used for dispatching this request.

        :return: Handler.
        """
        handler_name = "get" if self.state["request"].method == "HEAD" else self.state["request"].method.lower()
        h: t.Callable = getattr(self, handler_name)
        return h

    async def dispatch(self) -> None:
        """Dispatch a request."""
        app: BaseASGIService = self.state["app"]
        handler = await app.injector.inject(self.handler, self.state)
        return await concurrency.run(handler)
