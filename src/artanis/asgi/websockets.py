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

import starlette.websockets

if t.TYPE_CHECKING:
    from artanis.asgi import types

__all__ = ["WebSocket", "Close", "State"]

State = starlette.websockets.WebSocketState


class WebSocket(starlette.websockets.WebSocket):
    def __init__(self, scope: "types.Scope", receive: "types.Receive", send: "types.Send"):  # type: ignore[override]
        super().__init__(scope, receive, send)  # type: ignore[arg-type]

    @property
    def is_connecting(self) -> bool:
        """Check if websocket is connecting.

        :return: True if connecting.
        """
        return self.client_state == starlette.websockets.WebSocketState.CONNECTING

    @property
    def is_connected(self) -> bool:
        """Check if websocket is connected.

        :return: True if connected.
        """
        return self.client_state == starlette.websockets.WebSocketState.CONNECTED

    @property
    def is_disconnected(self) -> bool:
        """Check if websocket is disconnected.

        :return: True if disconnected.
        """
        return self.client_state == starlette.websockets.WebSocketState.DISCONNECTED


class Close(starlette.websockets.WebSocketClose):
    async def __call__(  # type: ignore[override]
        self, scope: "types.Scope", receive: "types.Receive", send: "types.Send"
    ) -> None:
        await super().__call__(scope, receive, send)  # type: ignore[arg-type]
