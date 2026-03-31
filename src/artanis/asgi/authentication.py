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

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from artanis.asgi.asgiservice import ASGIService
from artanis.asgi.asgiendpoint import BaseEndPoint, Descriptor, published


class AuthEndPoint(BaseEndPoint):
    descriptor = Descriptor()

    @published(path="/login", methods=["GET"])
    async def do_login(self, request: Request):
        return JSONResponse({'hello': 'world'})


class AuthAppService(ASGIService):

    def configure_services(self, config):
        self.mount('/auth', AuthEndPoint(config=config, parent=self))


app = AuthAppService.get_default_instance()
