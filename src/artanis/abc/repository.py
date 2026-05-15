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
from typing import Callable


class ClassRepository(dict[str, type[object] | None]):

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
