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
import functools
import typing as t

import starlette.middleware.authentication
import starlette.middleware.base
import starlette.middleware.cors
import starlette.middleware.gzip
import starlette.middleware.httpsredirect
import starlette.middleware.trustedhost

from artanis import concurrency
from artanis.asgi.debug.middleware import ExceptionMiddleware, ServerErrorMiddleware

if t.TYPE_CHECKING:
    from artanis.asgi import types
    from artanis.asgi.http import Request, Response
    from artanis.asgi.asgibase import BaseASGIService

__all__ = [
    "BaseHTTPMiddleware",
    "CORSMiddleware",
    "ExceptionMiddleware",
    "GZipMiddleware",
    "HTTPSRedirectMiddleware",
    "Middleware",
    "MiddlewareStack",
    "SessionMiddleware",
    "TrustedHostMiddleware",
]

try:
    import starlette.middleware.sessions

    class SessionMiddleware(starlette.middleware.sessions.SessionMiddleware):
        def __init__(self, app: types.App, *args, **kwargs):
            super().__init__(app, *args, **kwargs)  # type: ignore[arg-type]

        async def __call__(self, scope: types.Scope, receive: types.Receive, send: types.Send) -> None:  # type: ignore[overrid]
            return await super().__call__(scope, receive, send)  # type: ignore[assignment]

except ModuleNotFoundError:
    SessionMiddleware = None  # type: ignore[assignment]


class BaseHTTPMiddleware(starlette.middleware.base.BaseHTTPMiddleware):
    def __init__(self, app: types.App, *args, **kwargs):
        super().__init__(app, *args, **kwargs)  # type: ignore[arg-type]

    async def __call__(self, scope: types.Scope, receive: types.Receive, send: types.Send) -> None:  # type: ignore[overrid]
        return await super().__call__(scope, receive, send)  # type: ignore[assignment]


class CORSMiddleware(starlette.middleware.cors.CORSMiddleware):
    def __init__(self, app: types.App, *args, **kwargs):
        super().__init__(app, *args, **kwargs)  # type: ignore[arg-type]

    async def __call__(self, scope: types.Scope, receive: types.Receive, send: types.Send) -> None:  # type: ignore[overrid]
        return await super().__call__(scope, receive, send)  # type: ignore[assignment]


class GZipMiddleware(starlette.middleware.gzip.GZipMiddleware):
    def __init__(self, app: types.App, *args, **kwargs):
        super().__init__(app, *args, **kwargs)  # type: ignore[arg-type]

    async def __call__(self, scope: types.Scope, receive: types.Receive, send: types.Send) -> None:  # type: ignore[overrid]
        return await super().__call__(scope, receive, send)  # type: ignore[assignment]


class HTTPSRedirectMiddleware(starlette.middleware.httpsredirect.HTTPSRedirectMiddleware):
    def __init__(self, app: types.App, *args, **kwargs):
        super().__init__(app, *args, **kwargs)  # type: ignore[arg-type]

    async def __call__(self, scope: types.Scope, receive: types.Receive, send: types.Send) -> None:  # type: ignore[overrid]
        return await super().__call__(scope, receive, send)  # type: ignore[assignment]


class TrustedHostMiddleware(starlette.middleware.trustedhost.TrustedHostMiddleware):
    def __init__(self, app: types.App, *args, **kwargs):
        super().__init__(app, *args, **kwargs)  # type: ignore[arg-type]

    async def __call__(self, scope: types.Scope, receive: types.Receive, send: types.Send) -> None:  # type: ignore[overrid]
        return await super().__call__(scope, receive, send)  # type: ignore[assignment]


class Middleware:
    def __init__(self, middleware: "types.Middleware", **kwargs: t.Any) -> None:
        self.middleware = middleware
        self.kwargs = kwargs

    def __call__(self, app: types.App) -> "types.MiddlewareClass | types.App":
        return self.middleware(app, **self.kwargs)

    def __repr__(self) -> str:
        name = self.__class__.__name__
        middleware_name = (
            self.middleware.__class__.__name__
            if isinstance(self.middleware, types.MiddlewareClass)
            else self.middleware.__name__
        )
        args = ", ".join([middleware_name] + [f"{key}={value!r}" for key, value in self.kwargs.items()])
        return f"{name}({args})"


class MiddlewareStack:
    def __init__(self, app: BaseASGIService, middleware: t.Sequence[Middleware] | None = None, debug: bool = False):
        middleware: t.Sequence[Middleware] = middleware or []
        self.app = app
        self.middleware = list(reversed(middleware))
        self.debug = debug
        self._exception_handlers: dict[int | type[Exception], t.Callable[[Request, Exception], Response]] = {}
        self._stack: types.MiddlewareClass | types.App | None = None

    @property
    def stack(
        self,
    ) -> types.MiddlewareClass | types.App | None:
        if self._stack is None:
            self._stack = functools.reduce(
                lambda app, middleware: middleware(app=app),
                [
                    Middleware(ExceptionMiddleware, handlers=self._exception_handlers, debug=self.debug),
                    *self.middleware,
                    Middleware(ServerErrorMiddleware, debug=self.debug),
                ],
                self.app.router,
            )

        return self._stack

    @stack.deleter
    def stack(self):
        self._stack = None

    def add_exception_handler(
        self, key: int | type[Exception], handler: t.Callable[[Request, Exception], Response]
    ):
        """Adds a new handler for an exception type or a HTTP status code.

        :param key: Exception type or HTTP status code.
        :param handler: Exception handler.
        """
        self._exception_handlers[key] = handler
        del self.stack

    def add_middleware(self, middleware: Middleware):
        """Adds a new middleware to the stack.

        :param middleware: Middleware.
        """
        self.middleware.append(middleware)
        del self.stack

    async def __call__(self, scope: types.Scope, receive: types.Receive, send: types.Send) -> None:
        await concurrency.run(self.stack, scope, receive, send)
