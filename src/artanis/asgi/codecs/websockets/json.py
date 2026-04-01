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
import json
import typing as t

from artanis import exceptions
from artanis.asgi.codecs.base import WebsocketsCodec

if t.TYPE_CHECKING:
    from flama import types

__all__ = ["JSONCodec"]


class JSONCodec(WebsocketsCodec):
    encoding = "json"

    async def decode(self, item: "types.Message", **options):
        if item.get("text") is not None:
            text = item["text"]
        else:
            text = item["bytes"].decode("utf-8")

        try:
            return json.loads(text)
        except json.decoder.JSONDecodeError:
            raise exceptions.DecodeError("Malformed JSON data received")
