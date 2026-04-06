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

from artanis.asgi import schemas, http
from artanis.asgi.asgiendpoint import ASGIEndPoint, published, Descriptor
from artanis.asgi.asgiservice import ASGIService
from artanis.asgi.auth.handler import AuthenticationHandler
from artanis.asgi.auth.validator import APIAccessValidator
from artanis.asgi.http import APIResponse
from artanis.config import Configuration
from artanis.exceptions import HTTPException


class User(pydantic.BaseModel):
    username: str
    password: str


class AccessToken(pydantic.BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshToken(pydantic.BaseModel):
    token: str


class RefreshedToken(pydantic.BaseModel):
    access_token: str
    refresh_token: str


UserRequest = t.Annotated[schemas.Schema, schemas.SchemaMetadata(User)]
AccessTokenResponse = t.Annotated[schemas.Schema, schemas.SchemaMetadata(AccessToken)]

RefreshTokenRequest = t.Annotated[schemas.Schema, schemas.SchemaMetadata(RefreshToken)]
RefreshTokenResponse = t.Annotated[schemas.Schema, schemas.SchemaMetadata(RefreshedToken)]


class AuthDescriptor(Descriptor):
    default_tags = {}


class AuthEndPoint(ASGIEndPoint):
    descriptor = AuthDescriptor()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_handler = AuthenticationHandler(self.get_configuration())

    @published(path="/refresh", methods=["POST"])
    async def do_refresh(
            self,
            refresh: RefreshTokenRequest
    ) -> RefreshedToken:
        """
        tags:
            - Public
        title:
            Refresh access token
        description:
            Returns new user and refresh token to access protected endpoints
        responses:
            200:
                description:
                    Successful ping.
        """
        ...

    @published(path="/login", methods=["POST"])
    async def do_login(
            self,
            user: UserRequest,
    ) -> AccessTokenResponse:
        """
        tags:
            - Public
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
            raise HTTPException(status_code=500)
        User.model_validate(user)
        username = user.get("username")
        password = user.get("password")
        if not username or not password:
            raise HTTPException(status_code=401)
        result = await self.auth_handler.safe_execute(self.auth_handler.verify_user_auth, username, password)
        if not result:
            raise HTTPException(status_code=401)
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
        return APIResponse(status_code=http.HTTPStatus.OK, schema=types.Schema[AccessToken],
                           content=retval)


class MVCDescriptor(Descriptor):
    handle_request = True
    default_tags = {}


class MVCEndPoint(ASGIEndPoint):
    descriptor: Descriptor = MVCDescriptor()
    base_modules = "ecf.mvc"

    @published
    def hello_world(self, request: http.Request):
        print(request)
        return {'hello': 'world'}


class APIEndPoint(ASGIEndPoint):
    base_modules = "ecf.api"
    access_validator = APIAccessValidator()


class AuthAppService(ASGIService):

    def configure_services(self, config):
        self.mount('/auth', AuthEndPoint(config=config, parent=self))
        self.mount('/api', APIEndPoint(config=config, parent=self))
        self.mount('/mvc', MVCEndPoint(config=config, parent=self))


app = AuthAppService.get_default_instance()
