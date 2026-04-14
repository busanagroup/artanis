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
from starlette.staticfiles import StaticFiles

from artanis.asgi import schemas, http
from artanis.asgi.asgibase import BaseASGIService
from artanis.asgi.asgiendpoint import ASGIEndPoint, published, Descriptor
from artanis.asgi.asgiservice import ASGIService
from artanis.asgi.auth.handler import AuthenticationHandler
from artanis.asgi.auth.validator import APIAccessValidator
from artanis.asgi.http import Request, ArtanisStaticFiles
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
    refresh_token: str


UserRequest = t.Annotated[schemas.Schema, schemas.SchemaMetadata(User)]
AccessTokenResponse = t.Annotated[schemas.Schema, schemas.SchemaMetadata(AccessToken)]

RefreshTokenRequest = t.Annotated[schemas.Schema, schemas.SchemaMetadata(RefreshToken)]


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
                headers={"WWW-Authenticate": self.auth_handler.token_type}
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
                headers={"WWW-Authenticate": self.auth_handler.token_type}
            )
        User.model_validate(user)
        username = user.get("username")
        password = user.get("password")
        if not username or not password:
            raise HTTPException(
                status_code=401,
                detail="Insufficient permission",
                headers={"WWW-Authenticate": self.auth_handler.token_type}
            )
        result = await self.auth_handler.safe_execute(self.auth_handler.verify_user_auth, username, password)
        if not result:
            raise HTTPException(
                status_code=401,
                detail="Insufficient permission",
                headers={"WWW-Authenticate": self.auth_handler.token_type}
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


class MVCDescriptor(Descriptor):
    handle_request = True
    default_tags = {}


class MVCEndPoint(ASGIEndPoint):
    descriptor: Descriptor = MVCDescriptor()
    base_modules = "ecf.mvc"

    @published
    async def pgmredir(self, request: Request):
        return {'hello': "world"}

    @published
    async def verify(self, request: Request):
        return {'hello': "world"}

    @published
    async def definitions(self, request: Request):
        return {'hello': "world"}

    @published
    async def initialize(self, request: Request):
        return {'hello': "world"}

    @published
    async def open(self, request: Request):
        return {'hello': "world"}

    @published
    async def get(self, request: Request):
        return {'hello': "world"}

    @published
    async def post(self, request: Request):
        return {'hello': "world"}

    @published
    async def initexec(self, request: Request):
        return {'hello': "world"}

    @published
    async def execute(self, request: Request):
        return {'hello': "world"}

    @published
    async def print(self, request: Request):
        return {'hello': "world"}

    @published
    async def sync(self, request: Request):
        return {'hello': "world"}

    @published
    async def initlookup(self, request: Request):
        return {'hello': "world"}

    @published
    async def finalize(self, request: Request):
        return {'hello': "world"}

    @staticmethod
    def register_static(app: BaseASGIService):
        app.add_route("/", MVCEndPoint.frontend_view, include_in_schema=False)
        app.mount("/assets", ArtanisStaticFiles("asgi", "templates", "frontend", "assets"), name="assets")

    @staticmethod
    async def frontend_view():
        return http.ArtanisTemplateResponse("frontend/index.html", context=None)


class APIEndPoint(ASGIEndPoint):
    base_modules = "ecf.api"
    access_validator = APIAccessValidator()


class AuthAppService(ASGIService):

    def configure_services(self, config):
        self.mount('/auth', AuthEndPoint(config=config, parent=self))
        self.mount('/api', APIEndPoint(config=config, parent=self))
        self.mount('/mvc', MVCEndPoint(config=config, parent=self))
        MVCEndPoint.register_static(self)


app = AuthAppService.get_default_instance()
