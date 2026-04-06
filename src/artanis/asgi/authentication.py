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
import uuid

import pydantic

from artanis.asgi import schemas, http
from artanis.asgi.asgiendpoint import ASGIEndPoint, published, Descriptor
from artanis.asgi.asgiservice import ASGIService
from artanis.asgi.auth.jwt import jwt
from artanis.asgi.auth.validator import APIAccessValidator
from artanis.config import Configuration
from artanis.exceptions import HTTPException


class User(pydantic.BaseModel):
    username: str = None
    password: str = None


class UserToken(pydantic.BaseModel):
    token: str


UserRequest = t.Annotated[schemas.Schema, schemas.SchemaMetadata(User)]
UserResponse = t.Annotated[schemas.Schema, schemas.SchemaMetadata(UserToken)]


class AuthDescriptor(Descriptor):
    default_tags = {}


class AuthEndPoint(ASGIEndPoint):
    descriptor = AuthDescriptor()

    @published(path="/login", methods=["POST"])
    async def do_login(
            self,
            user: UserRequest
    ) -> UserResponse:
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
        config: Configuration = Configuration.get_default_instance(create_instance=False)
        if not config.server_is_ready:
            raise HTTPException()
        jwt_secret = config.get_property_value(config.JWT_SECRET_KEY, str(uuid.UUID(int=0)))
        jwt_token = jwt.JWT(
            {"alg": "HS256", "typ": "JWT"},
            {
                "data": {
                    "user_id": "admin",
                    "permissions": ["access:secure"],
                },
                "iat": 0,
            },
        )

        token_string = jwt_token.encode(jwt_secret.encode()).decode()
        # APIResponse(status_code=http.HTTPStatus.OK, schema=types.Schema[UserToken],
        #                            content={'token': token_string})
        retval = {"access_token": token_string}
        UserToken.model_validate(retval)
        return retval


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
