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
import logging
import typing as t
from importlib import import_module

from artanis.asgi.auth import exceptions
from artanis.asgi.auth.components import *  # noqa
from artanis.asgi.types import UserInfo

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class Payload:
    data: dict[str, t.Any]

    def __init__(
            self,
            data: dict[str, t.Any] | None = None
    ) -> None:
        object.__setattr__(self, "data", {**(data or {})})

    def to_dict(self) -> dict[str, t.Any]:
        return dataclasses.asdict(
            self, dict_factory=lambda x: {k: v for k, v in sorted(x, key=lambda y: y[0]) if v is not None}
        )


@dataclasses.dataclass(frozen=True)
class APIKey:
    sqlentity: t.ClassVar[t.Any]
    payload: Payload = dataclasses.field(init=False)

    def __init__(
            self, _payload: Payload | dict[str, t.Any] | None = None
    ) -> None:
        object.__setattr__(self, "payload", _payload if isinstance(_payload, Payload) else Payload(**(_payload or {})))

    def encode(self, key: bytes) -> bytes:
        raise NotImplementedError

    @classmethod
    async def decode(cls, token: bytes) -> t.Self:
        try:
            efusrs = cls.get_sqlentity().get_entity("efusrs")
            record = await cls.safe_execute(efusrs.get_user_api_key, token.decode())
            if not record:
                raise exceptions.Unauthorized("Invalid API key")

            fields = [field.name for field in dataclasses.fields(UserInfo)]
            data = dict(zip(fields, record))
            decoded_token = cls(_payload=dict(data=data))
        except exceptions.Unauthorized:
            logger.debug("Invalid API key")
            raise
        return decoded_token

    @classmethod
    def get_sqlentity(cls):
        if not hasattr(cls, 'sqlentity'):
            cls.sqlentity = import_module("artanis.sqlentity.entity")
        return cls.sqlentity

    @classmethod
    def get_entity(cls, tbname: str) -> t.Any:
        return cls.get_sqlentity().get_entity(tbname)

    @classmethod
    async def safe_execute(cls, func: t.Callable[..., t.Any], *args, **kwargs) -> t.Any:
        return await cls.get_sqlentity().safe_execute(func, *args, **kwargs)
