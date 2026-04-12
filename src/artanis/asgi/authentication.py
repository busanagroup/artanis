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
from __future__ import annotations

from typing import Any

import pydantic
from fastapi import Depends, Body, Request
from fastapi.security import OAuth2PasswordRequestForm
from starlette.exceptions import HTTPException

from artanis.asgi.asgiendpoint import ASGIEndPoint, Descriptor, published
from artanis.asgi.asgiservice import ASGIService
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


class AuthDescriptor(Descriptor):
    default_tags = {}


class AuthEndPoint(ASGIEndPoint):
    descriptor = AuthDescriptor()

    @published(path="/hello")
    async def hello(self):
        return {"message": "Hello World"}

    @published(path="/refresh", methods=["POST"], response_model=AccessToken)
    async def do_refresh(
            self,
            refresh_token: str = Body(...)
    ) -> Any:
        config: Configuration = self.get_configuration()
        if not config.server_is_ready:
            raise HTTPException(
                status_code=500,
                detail="Server is not ready",
                headers={"WWW-Authenticate": self.auth_handler.token_type}
            )
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

    @published(path="/login", methods=["POST"], response_model=AccessToken)
    async def do_login(
            self,
            form_data: OAuth2PasswordRequestForm = Depends(),
    ) -> Any:
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
        klass = request.scope.get("module_class")
        config: Configuration = self.get_configuration()
        if not klass:
            raise HTTPException(
                status_code=404, detail="PGMREDIR endpoint requires 'module_class' scope"
            )
        instance = klass(config=config, request=request)
        return await instance.hello()

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


class APIEndPoint(ASGIEndPoint):
    base_modules = "ecf.api"
    # access_validator = APIAccessValidator()


class AuthAppService(ASGIService):

    def configure_services(self, config):
        self.mount('/auth', AuthEndPoint(config=config, parent=self))
        self.mount('/api', APIEndPoint(config=config, parent=self))
        self.mount('/mvc', MVCEndPoint(config=config, parent=self))


app = AuthAppService.get_default_instance()
