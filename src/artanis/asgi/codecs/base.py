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
import abc
import typing as t

if t.TYPE_CHECKING:
    from artanis.asgi import http, types


Input = t.TypeVar("Input")
Output = t.TypeVar("Output")


class Codec(t.Generic[Input, Output], metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def decode(self, item: Input, **options) -> Output: ...


class HTTPCodec(Codec["http.Request", dict[str, t.Any] | None]):
    media_type: str | None = None


class WebsocketsCodec(Codec["types.Message", bytes | str | dict[str, t.Any] | None]):
    encoding: str | None = None
