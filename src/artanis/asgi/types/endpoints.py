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
    from artanis.asgi import types, websockets

__all__ = ["EndpointProtocol", "HTTPEndpointProtocol", "WebSocketEndpointProtocol"]


class EndpointProtocol(t.Protocol):
    def __init__(self, scope: "types.Scope", receive: "types.Receive", send: "types.Send") -> None: ...

    def __await__(self) -> t.Generator: ...

    @classmethod
    def allowed_handlers(cls) -> dict[str, t.Callable]: ...

    async def dispatch(self) -> None: ...


class HTTPEndpointProtocol(EndpointProtocol, t.Protocol):
    @classmethod
    def allowed_methods(cls) -> set[str]: ...

    @property
    def handler(self) -> t.Callable: ...


class WebSocketEndpointProtocol(EndpointProtocol, t.Protocol):
    encoding: "types.Encoding | None" = None

    async def on_connect(self, websocket: "websockets.WebSocket") -> None: ...

    async def on_receive(self, websocket: "websockets.WebSocket", data: "types.Data") -> None: ...

    async def on_disconnect(self, websocket: "websockets.WebSocket", websocket_code: "types.Code") -> None: ...
