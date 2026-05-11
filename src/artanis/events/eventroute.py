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

from artanis.abc.configurable import Configurable
from artanis.abc.objloader import ObjectLoader
from artanis.abc.objlock import SyncLock
from artanis.abc.singleton import Singleton
from artanis.config import Configuration
from artanis.utils import import_function

__all__ = ['EventRoute', 'event_route']


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


class EventRoute(Configurable, Singleton, SyncLock, ObjectLoader):

    def __init__(self, *args, base_modules: str = 'ecf.event', dynamic_load: bool = True, **kwargs):
        config = Configuration.get_default_instance(create_instance=False)
        super().__init__(*args, config=config, **kwargs)
        self.base_modules = base_modules
        self.dynamic_load = dynamic_load
        self.apply_lock = False
        self.__class_dir = None
        self.__all_classes = None

    @property
    def all_classes(self):
        return self.__all_classes

    def _load_class_dir(self):
        if (not self.base_modules) or self.__class_dir:
            return
        self.__class_dir = import_function(f"{self.base_modules}:__all__")

    def _load_classes(self):
        if (not self.base_modules) or self.__all_classes:
            return
        self.__all_classes = dict([(klass_name, self.__get_package_class(klass_name, self.base_modules)) \
                                   for klass_name in self.__class_dir]) \
            if not self.dynamic_load else HandlerRepository(
            [(klass_name, klass_name) for klass_name in self.__class_dir],
            base_modules=self.base_modules,
            package_func=self.__get_package_class
        )

    def __get_package_class(self, class_name: str, base_path: str | None = None, module_name: str | None = None):
        package = f"{self.base_modules if not base_path else base_path}.{class_name if not module_name else module_name}:{class_name}"
        return import_function(package)

    def do_configure(self):
        if not self.__all_classes:
            self._load_class_dir()
            self._load_classes()

    def get_event_handler(self, event_type: str) -> list[tuple[str, str]] | None:
        if not self.is_configured():
            self.configure()
        handler_list = []
        for name in self.all_classes.keys():
            klass = self.all_classes[name]
            if not klass:
                continue
            handlers = klass.get_event_handler(event_type)
            handler_list.extend(handlers)
        return handler_list


event_route = EventRoute()
