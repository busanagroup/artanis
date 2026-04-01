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

if t.TYPE_CHECKING:
    from artanis.asgi import endpoints

__all__ = [
    "Scope",
    "Message",
    "Receive",
    "Send",
    "AppClass",
    "AppFunction",
    "App",
    "MiddlewareClass",
    "MiddlewareFunction",
    "Middleware",
    "HTTPHandler",
    "WebSocketHandler",
    "Handler",
]

P = t.ParamSpec("P")
R = t.TypeVar("R", covariant=True)


class Scope(dict[str, t.Any]): ...


class Message(dict[str, t.Any]): ...


class Receive(t.Protocol):
    async def __call__(self) -> Message: ...


class Send(t.Protocol):
    async def __call__(self, message: Message) -> None: ...


# Applications
@t.runtime_checkable
class AppClass(t.Protocol):
    def __call__(self, scope: Scope, receive: Receive, send: Send) -> None | t.Awaitable[None]: ...


AppFunction = t.Callable[[Scope, Receive, Send], None | t.Awaitable[None]]
App = AppClass | AppFunction


# Middleware
@t.runtime_checkable
class MiddlewareClass(AppClass, t.Protocol[P, R]):
    def __init__(self, app: App, *args: P.args, **kwargs: P.kwargs): ...


MiddlewareFunction = t.Callable[t.Concatenate[App, P], App]
Middleware = type[MiddlewareClass] | MiddlewareFunction

HTTPHandler = t.Callable | type["endpoints.HTTPEndpoint"]
WebSocketHandler = t.Callable | type["endpoints.WebSocketEndpoint"]
Handler = HTTPHandler | WebSocketHandler
