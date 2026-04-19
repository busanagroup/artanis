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
from artanis.asgi.asgiendpoint import ASGIEndPoint, Descriptor, published
from artanis.asgi.auth.validator import AccessValidator
from artanis.asgi.services.mvcendpoint import MVCDescriptor


class MiscEndPoint(ASGIEndPoint):
    descriptor: Descriptor = MVCDescriptor
    base_path = "/misc"
    openapi_support = True
    access_validator = AccessValidator()

    @published(path="/menu")
    async def get_menu(self):
        return {"message": "pong"}
