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
from importlib import import_module
from typing import Callable, Any

from artanis.asgi.auth import AccessToken
from artanis.asgi.types import Scope
from artanis.exceptions import HTTPException


class AccessValidator:

    async def validate(self, scope: Scope, token: AccessToken): ...

    @property
    def sqlentity(self):
        if not hasattr(self, '_sqlentity'):
            self._sqlentity = import_module("artanis.sqlentity.entity")
        return self._sqlentity

    async def safe_execute(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        return await self.sqlentity.safe_execute(func, *args, **kwargs)

    def get_entity(self, tbname: str) -> Any:
        return self.sqlentity.get_entity(tbname)


class APIAccessValidator(AccessValidator):

    async def check_api_auth(self, usrname: str, svcname: str, fncname: str) -> bool:
        efurob = self.get_entity('efurob')
        efugrp = self.get_entity('efugrp')
        res = await efurob.check_public_access(svcname, fncname)
        if not res:
            grps = await efugrp.get_user_group(usrname)
            for grp in grps:
                res = await efurob.check_user_access(grp, svcname, fncname)
                if res:
                    break
        return res

    async def validate(self, scope: Scope, token: AccessToken):
        service_name = scope.get('module_path', '')[1:]
        func_name = scope.get('path')[1:]
        user_name = token.payload.data.get('user_id')
        if not await self.safe_execute(self.check_api_auth, user_name, service_name, func_name):
            raise HTTPException(status_code=403)


class MVCAccessValidator(AccessValidator):

    async def validate(self, scope: Scope, token: AccessToken): ...
