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
from datetime import datetime, timedelta, UTC
from importlib import import_module

from artanis.asgi.auth import RefreshToken
from artanis.asgi.auth.jwt import jwt
from artanis.asgi.auth.jwt.jwt import Header, Payload
from artanis.config import Configuration
from artanis.exceptions import HTTPException


class AuthenticationHandler:

    def __init__(self, config: Configuration):
        self.token_exp = int(config.get_property_value(config.JWT_TOKEN_EXPIRATION))
        self.refresh_exp = int(config.get_property_value(config.JWT_REFRESH_EXPIRATION))
        self.algorithm = config.get_property_value(config.JWT_ALGORITHM)
        self.secret_key = config.get_property_value(config.JWT_SECRET_KEY).encode()
        self.token_type = config.get_property_value(config.JWT_HEADER_PREFIX)

    @staticmethod
    def now() -> datetime:
        return datetime.now(UTC)

    def decode_token(self, token: str) -> RefreshToken:
        access_token = RefreshToken.decode(token.encode(), self.secret_key)
        if datetime.fromtimestamp(access_token.payload.exp) < datetime.now():
            raise HTTPException(
                status_code=401,
                detail="Token expired",
                headers={"WWW-Authenticate": self.token_type})
        user_id = access_token.payload.data.get("user_id")
        if user_id in [None, '']:
            raise HTTPException(
                status_code=403,
                detail="Invalid credential",
                headers={"WWW-Authenticate": self.token_type})
        return access_token

    def decode_refresh_token(self, token: str) -> RefreshToken:
        refresh_token = self.decode_token(token)
        if refresh_token.payload.jti != "refresh":
            raise HTTPException(
                status_code=406,
                detail="Token submitted was not a refresh token",
                headers={"WWW-Authenticate": self.token_type})
        return refresh_token

    def create_access_token(
            self,
            data: dict[str, t.Any] | None = None,
            now: datetime | None = None
    ):
        now = self.now() if now is None else now
        token_exp = now + timedelta(seconds=self.token_exp)
        jwt_token = jwt.JWT(
            _header=Header(
                typ="JWT",
                alg=self.algorithm
            ),
            _payload=Payload(
                data=data,
                iat=int(now.timestamp()),
                exp=int(token_exp.timestamp())
            )
        )
        return jwt_token.encode(self.secret_key).decode()

    def create_refresh_token(
            self,
            data: dict[str, t.Any] | None = None,
            now: datetime | None = None
    ):
        now = self.now() if now is None else now
        refresh_exp = now + timedelta(seconds=self.refresh_exp)
        jwt_token = jwt.JWT(
            _header=Header(
                typ="JWT",
                alg=self.algorithm
            ),
            _payload=Payload(
                data=data,
                iat=int(now.timestamp()),
                exp=int(refresh_exp.timestamp()),
                jti="refresh"
            )
        )
        return jwt_token.encode(self.secret_key).decode()

    async def verify_user_auth(self, usrname: str, passwd: str) -> bool:
        efusrs = self.get_entity('efusrs')
        return await efusrs.check_user_auth(user_name=usrname, passwd=passwd)

    @property
    def sqlentity(self):
        if not hasattr(self, '_sqlentity'):
            self._sqlentity = import_module("artanis.sqlentity.entity")
        return self._sqlentity

    def get_entity(self, tbname: str) -> t.Any:
        return self.sqlentity.get_entity(tbname)

    async def safe_execute(self, func: t.Callable[..., t.Any], *args, **kwargs) -> t.Any:
        return await self.sqlentity.safe_execute(func, *args, **kwargs)
