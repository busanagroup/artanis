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
from typing import Callable, Any, Sequence

from starlette.authentication import AuthCredentials

from artanis.asgi.types import Scope
from artanis.exceptions import HTTPException


class AccessValidator:

    async def validate(
            self,
            scope: Scope,
            required_permissions: Sequence[str]
    ):
        if not self.validate_permissions(scope, required_permissions):
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions")

    @staticmethod
    def validate_permissions(
            scope: dict[str, Any],
            required_permissions: Sequence[str]
    ) -> bool:
        credentials: AuthCredentials | None = scope.get("auth")
        for scope in required_permissions:
            if scope not in credentials.scopes:
                return False
        return True

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

    async def validate(
            self,
            scope: Scope,
            required_permissions: Sequence[str]
    ):
        await super().validate(scope, required_permissions)
        if not required_permissions:
            return
        user_name = scope['user'].display_name
        service_name = scope.get('module_path', '')[1:]
        func_name = scope.get('path')[1:]
        if not await self.safe_execute(self.check_api_auth, user_name, service_name, func_name):
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions")


class MVCAccessValidator(AccessValidator):

    async def validate_access(self, usrname: str, objname: str, acctype: str) -> bool:
        efumob = self.get_entity('efumob')
        efmxob = self.get_entity('efmxob')
        res = await efumob.verify_user_access(usrname, objname, acctype, acctp=False)
        return res if not res else await efmxob.verify_user_access(usrname, objname, acctype, acctp=False)

    async def verify_auth(
            self,
            usrname: str,
            objname: str,
            acctype: str
    ) -> bool:
        efumob = self.get_entity('efumob')
        efmxob = self.get_entity('efmxob')
        efugrp = self.get_entity('efugrp')
        res = await efumob.check_public_access(objname, acctype)
        if not res:
            grps = await efugrp.get_user_group(usrname)
            for grp in grps:
                res = await efumob.check_user_access(grp, objname, acctype)
                if res:
                    break
            if res:
                for grp in grps:
                    res = await efmxob.check_user_access(grp, objname, acctype)
                    if not res:
                        break
        else:
            res = await efmxob.check_user_access(usrname, objname, acctype)
        return res

    async def validate(
            self,
            scope: Scope,
            required_permissions: Sequence[str]
    ):
        await super().validate(scope, required_permissions)
        access_model = scope.get('auth_access_model', 0)
        if not required_permissions or access_model == 0:
            return
        user_name = scope["user"].display_name
        access_type = scope.get('auth_access_type', 'S')
        service_name = scope.get('module_path', '')[1:]
        func = self.validate_access if access_model == 1 else self.verify_auth
        if not await self.safe_execute(func, user_name, service_name, access_type):
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions")
