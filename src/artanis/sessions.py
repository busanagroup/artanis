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
import dataclasses

from starlette.authentication import AuthCredentials
from starlette.requests import Request

from artanis.asgi import types
from artanis.asgi.components.asgi import UserInfoComponent
from artanis.asgi.types import UserInfo


@dataclasses.dataclass
class UserSession:
    user_info: UserInfo
    permissions: AuthCredentials

    def to_dict(self):
        return dict(
            user_info=dict(
                username=self.user_info.username,
                first_name=self.user_info.first_name,
                last_name=self.user_info.last_name,
                email=self.user_info.email,
                cono=self.user_info.cono,
                coname=self.user_info.coname,
                dvno=self.user_info.dvno,
                dvname=self.user_info.dvname,
            ),
            permisssions= [*self.permissions.scopes],
        )

    @classmethod
    def from_dict(cls, user_info: dict) -> 'UserSession':
        user: dict = user_info.get("user_info", {})
        permissions: set = user_info.get("permisssions", set([]))
        user_info: UserInfo = UserInfo(
            username=user["username"],
            first_name=user.get("first_name"),
            last_name=user.get("last_name"),
            email=user.get("email"),
            cono=user.get("cono"),
            coname=user.get("coname"),
            dvno=user.get("dvno"),
            dvname=user.get("dvname")
        )
        credentials = AuthCredentials([*permissions])
        return UserSession(
            user_info=user_info,
            permissions=credentials
        )

    @classmethod
    async def from_request(cls, request: Request) -> 'UserSession':
        user_info_component = UserInfoComponent()
        auth_credentials: AuthCredentials = request.auth
        user_info = await user_info_component.resolve(request.scope)
        permissions = AuthCredentials([*auth_credentials.scopes])
        return UserSession(
            user_info=user_info,
            permissions=permissions
        )

    @classmethod
    async def from_scope(cls, scope: types.Scope) -> 'UserSession':
        user_info_component = UserInfoComponent()
        auth_credentials: AuthCredentials = scope.get("auth")
        child_scope = (auth_credentials.scopes if auth_credentials else []) or []
        user_info = await user_info_component.resolve(scope)
        permissions = AuthCredentials([*child_scope])
        return UserSession(
            user_info=user_info,
            permissions=permissions
        )
