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
from artanis import exceptions
from artanis.asgi.codecs.base import HTTPCodec, WebsocketsCodec
from artanis.asgi.codecs.websockets import BytesCodec

__all__ = ["ContentTypeNegotiator", "WebSocketEncodingNegotiator"]


class ContentTypeNegotiator:
    def __init__(self, codecs: list[HTTPCodec] | None = None):
        self.codecs = codecs or []

    def negotiate(self, content_type: str | None = None) -> HTTPCodec:
        """
        Given the value of a 'Content-Type' header, return the appropriate codec for decoding the request content.
        """
        if content_type is None:
            return self.codecs[0]

        content_type = content_type.split(";")[0].strip().lower()
        main_type = content_type.split("/")[0] + "/*"
        wildcard_type = "*/*"

        for codec in self.codecs:
            if codec.media_type in (content_type, main_type, wildcard_type):
                return codec

        raise exceptions.NoCodecAvailable(f"Unsupported media in Content-Type header '{content_type}'")


class WebSocketEncodingNegotiator:
    def __init__(self, codecs: list[WebsocketsCodec] | None = None):
        self.codecs = codecs or [BytesCodec()]

    def negotiate(self, encoding: str | None = None) -> WebsocketsCodec:
        """
        Given a websocket encoding, return the appropriate codec for decoding the request content.
        """
        if encoding is None:
            return self.codecs[0]

        for codec in self.codecs:
            if codec.encoding == encoding:
                return codec

        raise exceptions.NoCodecAvailable(f"Unsupported websocket encoding '{encoding}'")
