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

from artanis.asgi import types

if t.TYPE_CHECKING:
    from artanis.asgi.asgibase import BaseASGIService

__all__ = ["BaseEndpoint"]


class BaseEndpoint(types.EndpointProtocol):
    def __init__(self, scope: "types.Scope", receive: "types.Receive", send: "types.Send") -> None:
        """An endpoint.

        :param scope: ASGI scope.
        :param receive: ASGI receive function.
        :param send: ASGI send function.
        """
        app: BaseASGIService = scope["app"]
        scope["path"] = scope.get("root_path", "").rstrip("/") + scope["path"]
        scope["root_path"] = ""
        route, route_scope = app.router.resolve_route(scope)
        self.state = {
            "scope": route_scope,
            "receive": receive,
            "send": send,
            "exc": None,
            "app": app,
            "route": route,
        }

    def __await__(self) -> t.Generator:
        return self.dispatch().__await__()
