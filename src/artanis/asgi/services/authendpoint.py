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

import pydantic
from starlette.exceptions import HTTPException

from artanis.asgi import schemas, types
from artanis.asgi.asgiendpoint import Descriptor, ASGIEndPoint, published
from artanis.asgi.auth.handler import AuthenticationHandler
from artanis.asgi.auth.validator import AccessValidator
from artanis.config import Configuration


class User(pydantic.BaseModel):
    username: str
    password: str


class AccessToken(pydantic.BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshToken(pydantic.BaseModel):
    refresh_token: str


class UserInformation(pydantic.BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str | None
    cono: str | None
    coname: str | None
    dvno: str | None
    dvname: str | None


UserRequest = t.Annotated[schemas.Schema, schemas.SchemaMetadata(User)]
AccessTokenResponse = t.Annotated[schemas.Schema, schemas.SchemaMetadata(AccessToken)]

RefreshTokenRequest = t.Annotated[schemas.Schema, schemas.SchemaMetadata(RefreshToken)]

UserInformationResponse = t.Annotated[schemas.Schema, schemas.SchemaMetadata(UserInformation)]


class AuthDescriptor(Descriptor):
    default_tags = {}


class AuthEndPoint(ASGIEndPoint):
    descriptor = AuthDescriptor()
    base_path = "/auth"
    openapi_support = True
    access_validator = AccessValidator()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_handler = AuthenticationHandler(self.get_configuration())

    @published(path="/userinfo", methods=["GET"], tags={"permissions": ["access:secure"]})
    async def get_userinfo(
            self,
            userinfo: types.UserInfo
    ) -> UserInformationResponse:
        """
        tags:
            - Authentication
        title:
            Get user information
        description:
            Returns user information in detail
        responses:
            200:
                description:
                    Successful ping.
        """
        config: Configuration = self.get_configuration()
        if not config.server_is_ready:
            raise HTTPException(
                status_code=500,
                detail="Server is not ready",
                headers={"access-token": self.auth_handler.token_type}
            )
        result = await self.auth_handler.get_user_info(userinfo.username)
        if not result:
            raise HTTPException(
                status_code=401,
                detail="Insufficient permission",
                headers={"access-token": self.auth_handler.token_type}
            )
        retval = dict(zip(["username", "first_name", "last_name", "email", "cono", "coname", "dvno", "dvname"],
                          result))
        UserInformation.model_validate(retval)
        return retval

    @published(path="/refresh", methods=["POST"])
    async def do_refresh(
            self,
            refresh: RefreshTokenRequest
    ) -> AccessTokenResponse:
        """
        tags:
            - Authentication
        title:
            Refresh access token
        description:
            Returns new user and refresh token to access protected endpoints
        responses:
            200:
                description:
                    Successful ping.
        """
        config: Configuration = self.get_configuration()
        if not config.server_is_ready:
            raise HTTPException(
                status_code=500,
                detail="Server is not ready",
                headers={"access-token": self.auth_handler.token_type}
            )
        refresh_token = refresh.get("refresh_token")
        token = self.auth_handler.decode_refresh_token(refresh_token)
        username = token.payload.data.get("user_id")
        now = self.auth_handler.now()
        access_token = self.auth_handler.create_access_token(
            data=dict(
                user_id=username,
                permissions=["access:secure"]
            ),
            now=now
        )
        refresh_token = self.auth_handler.create_refresh_token(
            data=dict(
                user_id=username,
            ),
            now=now
        )
        retval = dict(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=self.auth_handler.token_type
        )
        AccessToken.model_validate(retval)
        return retval

    @published(path="/login", methods=["POST"])
    async def do_login(
            self,
            user: UserRequest,
    ) -> AccessTokenResponse:
        """
        tags:
            - Authentication
        title:
            Authenticate user
        description:
            Returns a user token to access protected endpoints
        responses:
            200:
                description:
                    Successful ping.
        """
        config: Configuration = self.get_configuration()
        if not config.server_is_ready:
            raise HTTPException(
                status_code=500,
                detail="Server is not ready",
                headers={"access-token": self.auth_handler.token_type}
            )
        User.model_validate(user)
        username: str = user.get("username")
        password: str = user.get("password")
        if not username or not password:
            raise HTTPException(
                status_code=401,
                detail="Insufficient permission",
                headers={"access-token": self.auth_handler.token_type}
            )
        result = await self.auth_handler.verify_user_auth(username, password)
        if not result:
            raise HTTPException(
                status_code=401,
                detail="Insufficient permission",
                headers={"access-token": self.auth_handler.token_type}
            )
        now = self.auth_handler.now()
        access_token = self.auth_handler.create_access_token(
            data=dict(
                user_id=username,
                permissions=["access:secure"]
            ),
            now=now
        )
        refresh_token = self.auth_handler.create_refresh_token(
            data=dict(
                user_id=username,
            ),
            now=now
        )
        retval = dict(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=self.auth_handler.token_type
        )

        AccessToken.model_validate(retval)
        return retval
