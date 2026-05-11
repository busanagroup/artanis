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
import inspect
from typing import Callable, Any

from lru import LRU as LRUDict

from artanis import concurrency
from artanis.config import Configuration
from artanis.events import BaseEvent
from artanis.utils import import_function

__all__ = ['EventDispatcher']


class HandlerRepository(dict[str, type[object] | None]):

    def __init__(self, *args, base_modules: str | None = None, package_func: Callable | None = None, **kwargs):
        self.base_modules = base_modules
        self.package_func = package_func
        super().__init__(*args, **kwargs)

    def __getitem__(self, item):
        value = super().__getitem__(item)
        return self.validate(item, value)

    def get(self, key: str, *args, **kwargs):
        value = super().get(key, *args, **kwargs)
        return self.validate(key, value)

    def values(self):
        return [self.get(item) for item in self.keys()]

    def validate(self, key, value):
        klass = value
        if isinstance(value, str):
            klass = self.package_func(value, self.base_modules)
            self.__setitem__(key, klass)
        return klass


class EventDispatcher:
    __base_module: str = 'ecf.event'
    __dynamic_load: bool = True
    __class_dir = None
    __all_classes = None
    __instances = LRUDict(size=32)
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
            if not cls.__dynamic_load else HandlerRepository(
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
        klass = cls.__all_classes[klass_name]
        if not klass:
            return None
        if klass.__name__ in cls.__instances:
            instance = cls.__instances[klass.__name__]
        else:
            instance = klass(config=cls.__config)
            cls.__instances[klass.__name__] = instance
        return instance

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
                params.append(klass.model_validate_json(event))
        await concurrency.run(func, *params)


