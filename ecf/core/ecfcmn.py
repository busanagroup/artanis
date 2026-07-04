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

import asyncio
import threading
from typing import Mapping, Any, TYPE_CHECKING, Type

from lru import LRU as LRUDict

from artanis.abc.classprops import classproperty
from artanis.abc.repository import ClassRepository
from artanis.asgi.asgiendpoint import ControllerABC
from artanis.component.validators import validators
from artanis.config import Configuration
from artanis.sqlentity import entity, Entity
from artanis.taskiq.proxy import TaskObjectProxy
from artanis.utils import import_function

if TYPE_CHECKING:
    from ecf.core.jobsvc import JobEngine, JOBSession


class CounterMeta(type):
    __counter: int = 0
    __lock: asyncio.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        super().__call__(*args, **kwargs)
        instance = type.__new__(cls, *args, **kwargs)
        instance.__counter = CounterMeta.__counter
        CounterMeta.__lock.acquire()
        try:
            CounterMeta.__counter += 1
        finally:
            CounterMeta.__lock.release()
        return instance


class ECFObject(object):
    pass


class SupportClass:

    @staticmethod
    async def record_exist(table_name: str, *args, **kwargs):
        return await entity.record_exist(table_name, *args, **kwargs)

    @staticmethod
    async def validate_existence(entity_obj):
        return await entity.validate_existence(entity_obj)

    @staticmethod
    async def ensure_record_exist(self, entity_obj, msg):
        record_status = await entity.validate_existence(entity_obj)
        validators.Assertion(messages={'assert': msg}).to_python(record_status)

    @staticmethod
    async def ensure_record_not_exist(self, entity_obj, msg):
        record_status = await entity.validate_existence(entity_obj)
        validators.Assertion(messages={'assert': msg}).to_python(not record_status)

    @staticmethod
    def get_entity(table_name: str) -> Type[Entity]:
        return entity.get_entity(table_name)

    @staticmethod
    async def get_program_redirection(cono: str, prgcode: str, dvcode: str):
        csyinf = entity.get_entity('csyinf')
        obj = await csyinf.get(cono, ' ' * 3, 'PRGRDRC', prgcode, dvcode)
        return prgcode if (obj is None) or (obj.cinft241 in [None, '']) else obj.cinft241

    @staticmethod
    def get_entity_field_info(entity, field_name: str):
        return entity.get_entity_field_info(entity, field_name)

    @staticmethod
    def get_field_list(model):
        return model.get_field_list()

    @staticmethod
    async def get_field_values(obj, adict=None):
        adict = entity.init_field_dict(obj.__class__) if adict is None else adict
        await entity.get_field_values(obj, adict)
        return adict

    @staticmethod
    async def set_field_values(adict, obj):
        await entity.set_field_values(adict, obj)

    @staticmethod
    async def get_recordset(table_name: str, *args, **kwargs):
        return await entity.get_recordset(table_name, *args, **kwargs)

    @staticmethod
    async def get_audit_recordset(table_name: str, *args, **kwargs):
        return await entity.get_audit_recordset(table_name, *args, **kwargs)

    @staticmethod
    def get_unmapped_fields(fields, model):
        return model.get_unmapped_fields(fields)

    @classproperty
    def bo_proxy(cls):
        return BusinessObjectProxy

    @staticmethod
    def get_session():
        return entity.get_session()

    @staticmethod
    def get_task_service(username: str, service_name: str):
        return TaskObjectProxy(username, service_name)


class BaseController(ControllerABC, SupportClass):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service_name = self.__class__.__name__

    async def get_username(self):
        raise NotImplementedError

    def get_service_name(self) -> str:
        return self.service_name


class BusinessObjectProxy:
    __base_module: str = 'ecf.bo'
    __configured: bool = False
    __config: Configuration = None
    __class_dir = None
    __all_classes: Mapping[str, Any] = None
    __dynamic_load: bool = True
    __instances = LRUDict(size=32)

    @classmethod
    def get_object(cls, service_name: str, instantiate: bool = True) -> Any:
        cls._ensure_configured()
        if not (service_name in cls.__class_dir):
            raise NameError(f"Object [{service_name}] is not available")
        klass = cls.__all_classes[service_name]
        if not instantiate:
            return klass
        if klass.__name__ in cls.__instances:
            instance = cls.__instances[klass.__name__]
        else:
            instance = klass(config=cls.__config)
            cls.__instances[klass.__name__] = instance
        return instance

    @classmethod
    def class_exist(cls, klass_name: str) -> bool:
        return klass_name in cls.__class_dir

    @classmethod
    def _ensure_configured(cls):
        if not cls.__configured:
            cls.configure()

    @classmethod
    def configure(cls):
        if cls.__configured:
            return
        try:
            cls._load_class_dir()
            cls._load_classes()
            cls.__config = Configuration.get_default_instance(create_instance=False)
        finally:
            cls.__configured = True

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
        return import_function(f"{cls.__base_module \
            if not base_path else base_path}.{class_name \
            if not module_name else module_name}:{class_name}")


class JobObjectHandler(BusinessObjectProxy):
    __base_module: str = 'ecf.job'
    __configured: bool = False
    __config: Configuration = None
    __class_dir = None
    __all_classes: Mapping[str, Any] = None
    __dynamic_load: bool = True
    __instances = LRUDict(size=32)

    @classmethod
    async def execute_job(cls, service_name: str, session: 'JOBSession'):
        instance: 'JobEngine' = cls.get_object(service_name)
        return await instance.execute(session)

    @classmethod
    def get_service_class(cls, service_name: str):
        return cls.get_object(service_name, instantiate=False)

    @classmethod
    def get_object(cls, service_name: str, instantiate: bool = True) -> Any:
        cls._ensure_configured()
        if not (service_name in cls.__class_dir):
            raise NameError(f"Object [{service_name}] is not available")
        klass = cls.__all_classes[service_name]
        if not instantiate:
            return klass
        if klass.__name__ in cls.__instances:
            instance = cls.__instances[klass.__name__]
        else:
            instance = klass(config=cls.__config)
            cls.__instances[klass.__name__] = instance
        return instance

    @classmethod
    def class_exist(cls, klass_name: str) -> bool:
        return klass_name in cls.__class_dir

    @classmethod
    def _ensure_configured(cls):
        if not cls.__configured:
            cls.configure()

    @classmethod
    def configure(cls):
        if cls.__configured:
            return
        try:
            cls._load_class_dir()
            cls._load_classes()
            cls.__config = Configuration.get_default_instance(create_instance=False)
        finally:
            cls.__configured = True

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
        return import_function(f"{cls.__base_module \
            if not base_path else base_path}.{class_name \
            if not module_name else module_name}:{class_name}")

