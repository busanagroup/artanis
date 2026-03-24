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

from typing import Any

from starlette.datastructures import URLPath
from starlette.routing import BaseRoute, Match
from starlette.types import Scope, Receive, Send

from artanis.abc.configurable import Configurable
from artanis.sqlentity import safe_execute as safe_exec

class ArtanisEndPoint(BaseRoute, Configurable):

    def matches(self, scope: Scope) -> tuple[Match, Scope]:
        raise NotImplementedError

    def url_path_for(self, name: str, /, **path_params: Any) -> URLPath:
        raise NotImplementedError

    def handle(self, scope: Scope, receive: Receive, send: Send) -> None:
        raise NotImplementedError

    @staticmethod
    async def safe_execute(func, *args, **kwargs):
        return await safe_exec(func, *args, **kwargs)
