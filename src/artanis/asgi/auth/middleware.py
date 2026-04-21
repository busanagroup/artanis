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
import http
import logging
import re
import typing as t

from artanis import exceptions
from artanis.asgi import auth
from artanis.asgi.auth.authentication import AuthenticationBackend
from artanis.asgi.auth.validator import AccessValidator
from artanis.asgi.http import APIErrorResponse, Request
from artanis.exceptions import HTTPException

if t.TYPE_CHECKING:
    from artanis.asgi.asgibase import BaseASGIService
    from artanis.asgi import types
    from artanis.asgi.http import Response

__all__ = ["AuthenticationMiddleware"]

logger = logging.getLogger(__name__)


class AuthenticationMiddleware:
    def __init__(self, app: "types.App", *, ignored: list[str] = None, backend: AuthenticationBackend = None) -> None:
        ignored = ignored or []
        self.app: BaseASGIService = t.cast("BaseASGIService", app)
        self.backend: AuthenticationBackend = backend
        self._ignored = [re.compile(x) for x in ignored]

    async def __call__(self, scope: "types.Scope", receive: "types.Receive", send: "types.Send") -> None:
        if scope["type"] not in ("http", "websocket") or any(pattern.match(scope["path"]) for pattern in self._ignored):
            await self.app(scope, receive, send)
            return

        response = await self.backend.authenticate(self, scope, receive)
        await response(scope, receive, send)

