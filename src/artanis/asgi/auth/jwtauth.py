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
import typing as t

from starlette.authentication import UnauthenticatedUser, AuthCredentials

from artanis.asgi import auth
from artanis.asgi.auth.authentication import AuthenticationBackend, ArtanisUser
from artanis.asgi.http import Request
from artanis.exceptions import HTTPException

if t.TYPE_CHECKING:
    from artanis.asgi.asgibase import BaseASGIService
    from artanis.asgi import types

logger = logging.getLogger(__name__)


class JWTAuthBackend(AuthenticationBackend):

    def __init__(self, tag: str = "permissions") -> None:
        self._tag = tag

    async def authenticate(self, sender, scope: "types.Scope", receive: "types.Receive"):
        app: BaseASGIService = scope["app"]
        try:
            token: auth.AccessToken = await app.injector.value(
                auth.AccessToken, {"request": Request(scope, receive=receive)}
            )
            user_name: str = token.payload.data.get('user_id')
            child_scope = dict(
                user=ArtanisUser(user_name, token.payload.data),
                auth=AuthCredentials(["access:secure"]),
            )
        except HTTPException:
            try:
                token: auth.APIKeyToken = await app.injector.value(
                    auth.APIKeyToken, {"request": Request(scope, receive=receive)}
                )
                user_name: str = token.payload.data.get('username')
                child_scope = dict(
                    user=ArtanisUser(user_name, token.payload.data),
                    auth=AuthCredentials(["access:secure"]),
                )
            except HTTPException:
                child_scope = dict(
                    user=UnauthenticatedUser(),
                    auth=AuthCredentials([]),
                )
        return sender.app, child_scope
