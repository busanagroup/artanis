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
from artanis.asgi.auth.validator import AccessValidator
from artanis.asgi.http import APIErrorResponse, Request
from artanis.exceptions import HTTPException

if t.TYPE_CHECKING:
    from artanis.asgi.asgiservice import ASGIService
    from artanis.asgi import types
    from artanis.asgi.http import Response

__all__ = ["AuthenticationMiddleware"]

logger = logging.getLogger(__name__)


class AuthenticationMiddleware:
    def __init__(self, app: "types.App", *, tag: str = "permissions", ignored: list[str] = []):
        self.app: ASGIService = t.cast("ASGIService", app)
        self._tag = tag
        self._ignored = [re.compile(x) for x in ignored]

    async def __call__(self, scope: "types.Scope", receive: "types.Receive", send: "types.Send") -> None:
        if scope["type"] not in ("http", "websocket") or any(pattern.match(scope["path"]) for pattern in self._ignored):
            await self.app(scope, receive, send)
            return

        response = await self.get_auth_response(scope, receive)

        await response(scope, receive, send)

    async def get_auth_response(self, scope: "types.Scope", receive: "types.Receive") -> "Response | ASGIService":
        app: ASGIService = scope["app"]
        try:
            route, route_scope = app.router.resolve_route(scope)
            permissions = set(route.tags.get(self._tag, []))
        except (exceptions.MethodNotAllowedException, exceptions.NotFoundException):
            permissions = []

        if not (required_permissions := set(permissions)):
            return self.app

        try:
            token: auth.AccessToken = await app.injector.value(
                auth.AccessToken, {"request": Request(scope, receive=receive)}
            )
        except HTTPException as e:
            logger.debug("JWT error: %s", e.detail)
            return APIErrorResponse(status_code=e.status_code, detail=e.detail)

        user_permissions = set(token.payload.data.get("permissions", [])) | {
            y for x in token.payload.data.get("roles", {}).values() for y in x
        }
        if not (user_permissions >= required_permissions):
            logger.debug("User does not have the required permissions: %s", required_permissions)
            return APIErrorResponse(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail="Insufficient permissions"
            )

        validator: AccessValidator = route_scope.get('access_validator', None)
        if not validator:
            return self.app

        try:
            child_scope = await validator.validate(route_scope, token)
            if child_scope:
                scope.update(child_scope)
        except HTTPException as exc:
            return APIErrorResponse(
                status_code=exc.status_code,
                detail=exc.detail,
                headers=exc.headers,
            )

        return self.app
