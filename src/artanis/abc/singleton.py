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

__all__ = ['Singleton', 'AsyncSingleton']

from .objlock import BaseLocker


class Singleton(BaseLocker):
    VM_DEFAULT = None

    def _configure_instance(self, *args, **kwargs):
        ...

    @classmethod
    def has_singleton_instance(cls):
        return cls.VM_DEFAULT is not None

    @classmethod
    def get_default_instance(cls, *args, create_instance=True, **kwargs):
        cls.get_class_locker().acquire()
        try:
            if create_instance and not cls.has_singleton_instance():
                cls.VM_DEFAULT = object.__new__(cls)
                cls.VM_DEFAULT.__init__()
                cls.VM_DEFAULT._configure_instance(*args, **kwargs)
            return cls.VM_DEFAULT
        finally:
            cls.get_class_locker().release()

    @classmethod
    def get_singleton(cls):
        instance = cls.get_default_instance(create_instance=False)
        if not instance:
            raise Exception(f"{str(cls)} has not been created previously")
        return instance


class AsyncSingleton(BaseLocker):
    VM_DEFAULT = None

    async def _configure_instance(self, *args, **kwargs):
        ...

    @classmethod
    def has_singleton_instance(cls):
        return cls.VM_DEFAULT is not None

    @classmethod
    async def get_default_instance(cls, *args, create_instance=True, **kwargs):
        await cls.get_class_locker().acquire()
        try:
            if create_instance and not cls.has_singleton_instance():
                cls.VM_DEFAULT = object.__new__(cls)
                cls.VM_DEFAULT.__init__()
                await cls.VM_DEFAULT._configure_instance(*args, **kwargs)
            return cls.VM_DEFAULT
        finally:
            cls.get_class_locker().release()
