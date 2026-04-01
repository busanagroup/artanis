#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2025 Busana Apparel Group. All rights reserved.
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

from artanis import exceptions
from artanis.asgi.codecs.base import HTTPCodec

if t.TYPE_CHECKING:
    from artanis.asgi import http

__all__ = ["JSONDataCodec"]


class JSONDataCodec(HTTPCodec):
    media_type = "application/json"
    format = "json"

    async def decode(self, item: "http.Request", **options) -> dict[str, t.Any] | None:
        try:
            if await item.body() == b"":
                return None

            return await item.json()
        except ValueError as exc:
            raise exceptions.DecodeError(f"Malformed JSON. {exc}") from None
