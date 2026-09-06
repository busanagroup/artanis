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
import inspect
from functools import lru_cache
from typing import Any

from artanis import concurrency
from artanis.abc.repository import ClassRepository
from artanis.config import Configuration
from artanis.events import BaseEvent
from artanis.utils import import_function

__all__ = ['EventDispatcher']


class EventDispatcher:
    __base_module: str = 'ecf.event'
    __dynamic_load: bool = True
    __class_dir = None
    __all_classes = None
    __config: Configuration = None

    @classmethod
    def _load_class_dir(cls):
        if (not cls.__base_module) or cls.__class_dir:
            return
        cls.__class_dir = import_function(f"{cls.__base_module}:__all__")

    @classmethod
    def _load_classes(cls):
        if (not cls.__base_module) or cls.__all_classes:
            return
        cls.__all_classes = dict([(klass_name, cls.__get_package_class(klass_name, cls.__base_module)) \
                                  for klass_name in cls.__class_dir]) \
            if not cls.__dynamic_load else ClassRepository(
            [(klass_name, klass_name) for klass_name in cls.__class_dir],
            base_modules=cls.__base_module,
            package_func=cls.__get_package_class
        )

    @classmethod
    def __get_package_class(cls, class_name: str, base_path: str | None = None, module_name: str | None = None):
        package = f"{cls.__base_module if not base_path else base_path}.{class_name if not module_name else module_name}:{class_name}"
        return import_function(package)

    @classmethod
    def get_class_instance(cls, klass_name: str) -> Any:
        return None if klass_name not in cls.__all_classes else cls._instantiate(klass_name)

    @classmethod
    @lru_cache(maxsize=8)
    def _instantiate(cls, klass_name: str) -> Any:
        klass = cls.__all_classes[klass_name]
        return klass(config=cls.__config)

    @classmethod
    def configure(cls):
        if not cls.__all_classes:
            cls._load_class_dir()
            cls._load_classes()
            cls.__config = Configuration.get_default_instance(create_instance=False)

    @classmethod
    async def dispatch(cls, klass_name: str, func_name: str, event: bytes):
        cls.configure()
        instance = cls.get_class_instance(klass_name)
        func = getattr(instance, func_name)
        params = []
        for parameter in [
            x
            for x in inspect.signature(func).parameters.values()
            if not (x.name in ("self", "cls", "args", "kwargs") and x.annotation == inspect._empty)
        ]:
            if issubclass(parameter.annotation, BaseEvent):
                klass = parameter.annotation
                params.append(klass.model_validate(event))
        await concurrency.run(func, *params)
