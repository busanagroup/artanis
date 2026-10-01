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

from artanis.asgi.asgiendpoint import Descriptor
from artanis.config import Configuration
from artanis.sqlentity import entity
from artanis.sqlentity.sqlorm import Entity
from ecf.core.ecfcmn import BaseController


class MVCModelBinder:

    def __init__(self, model_class: type | str):
        self.model_class: Entity = entity.get_entity(model_class) if isinstance(model_class, str) else model_class

    async def get(self, **kwargs):
        if not kwargs:
            return self.model_class.get_all()

        try:
            return await self.model_class.get(**kwargs)
        except self.model_class.DoesNotExist:
            return await self.model_class.filter(**kwargs).first()

    async def get_filter(self, **kwargs):
        return await self.model_class.filter(**kwargs).all()

    async def create(self, **kwargs):
        return await self.model_class.create(**kwargs)

    async def delete(self, **kwargs):
        obj = await self.get(**kwargs)
        if obj:
            await obj.delete()
            return True
        return False


class MVCDescriptor(Descriptor):
    ...


class MVCBaseService(BaseController):
    __config: Configuration
    __label: str
    __binder: MVCModelBinder | None
    descriptor = MVCDescriptor

    def __init_subclass__(cls, **kwargs):
        entity = kwargs.pop('entity', None)
        cls.__binder = MVCModelBinder(entity) if entity else None
        cls.__label = kwargs.pop('label', None)
        cls.__config = Configuration.get_default_instance(create_instance=False)
        super().__init_subclass__(**kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MVCService(MVCBaseService):
    description: str
