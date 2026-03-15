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
from __future__ import annotations

__all__ = ['BaseObjectLoader', 'BaseObjectCreator', 'ObjectLoader', 'ObjectCreator', 'AsyncObjectCreator']

import logging
from typing import Any


class BaseObjectLoader(object):

    def __init__(self, *args, **kwargs):
        super(BaseObjectLoader, self).__init__()

    @classmethod
    def __get_klass__(cls, components, modules):
        mod = None
        try:
            mod = __import__(modules)
            for comp in components[1:]:
                mod = getattr(mod, comp)
        except Exception as ex:
            logging.exception(ex)
        return mod


class ObjectLoader(BaseObjectLoader):

    def _verify_klass(self, klass, class_name):
        return klass

    @classmethod
    def _get_klass_module(cls, class_name: str) -> tuple:
        components = class_name.split(".")
        return components, ".".join(components[:-1])

    def _get_existing_klass(self, class_name: str) -> object:
        return None

    def _validate_classname(self, class_name, **kwargs):
        return class_name

    def _get_klass(self, class_name: Any, **kwargs) -> Any:
        klass_name = self._validate_classname(class_name, **kwargs)
        mod = self._get_existing_klass(klass_name)
        if not mod:
            components, import_modules = self._get_klass_module(klass_name)
            mod = self.__get_klass__(components, import_modules)
            mod = self._verify_klass(mod, klass_name)
        return mod


class BaseObjectCreator(object):

    def __init__(self, *args, **kwargs):
        super(BaseObjectCreator, self).__init__(*args, **kwargs)

    @classmethod
    def __create_instance__(cls, klass):
        instance = object.__new__(klass)
        instance.__init__()
        return instance


class ObjectCreator(BaseObjectCreator):

    def _configure_instance(self, klass, instance, *args, **kwargs):
        return instance

    def _create_instance(self, klass, *args, **kwargs):
        if not klass:
            return None
        instance = self.__create_instance__(klass)
        instance = self._configure_instance(klass, instance, *args, **kwargs)
        return instance


class AsyncObjectCreator(BaseObjectCreator):

    def __init__(self):
        super(AsyncObjectCreator, self).__init__()

    async def _configure_instance(self, klass, instance, *args, **kwargs):
        return instance

    async def _create_instance(self, klass, *args, **kwargs):
        if not klass:
            return None
        instance = self.__create_instance__(klass)
        return await self._configure_instance(klass, instance, *args, **kwargs)
