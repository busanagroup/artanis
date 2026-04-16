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
from starlette.requests import Request

from artanis.asgi.asgiendpoint import Descriptor, ASGIEndPoint, published
from artanis.asgi.auth.validator import MVCAccessValidator
from artanis.asgi.types import UserInfo


class MVCDescriptor(Descriptor):
    handle_request = True
    # default_tags = {}


class MVCEndPoint(ASGIEndPoint):
    descriptor: Descriptor = MVCDescriptor()
    base_modules = "ecf.mvc"
    base_path = "/mvc"
    openapi_support = True
    access_validator = MVCAccessValidator()

    @published
    async def pgmredir(self, request: Request):
        return {'hello': "world"}

    @published
    async def verify(self, request: Request):
        return {'hello': "world"}

    @published
    async def definitions(self, userinfo: UserInfo, request: Request):
        return {'hello': f"{userinfo.username}"}

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
