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
from artanis.asgi import http
from artanis.asgi.asgibase import BaseASGIService
from artanis.asgi.asgiendpoint import ASGIEndPoint
from artanis.asgi.http import ArtanisStaticFiles


class StaticEndPoint(ASGIEndPoint):
    @classmethod
    def register(cls, app: BaseASGIService):
        app.add_route("/", cls.frontend_view, include_in_schema=False)
        app.mount("/assets", ArtanisStaticFiles("asgi", "templates", "frontend", "assets"), name="assets")

    @staticmethod
    async def frontend_view():
        return http.ArtanisTemplateResponse("frontend/index.html", context=None)
