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

from http.cookiejar import user_domain_match

from artanis.asgi.asgiendpoint import ControllerABC
from artanis.component.validators import validators
from artanis.sqlentity import entity
from artanis.utils import import_function
from ecf.core.ecfexceptions import ECFServiceError


class ECFObject(object):
    pass


class SupportClass(ControllerABC):

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
    def get_entity(table_name: str):
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
    def get_field_list(cls):
        return entity.get_field_list(cls)

    @staticmethod
    async def get_field_values(obj, adict=None):
        adict = entity.get_field_list(obj.__class__) if adict is None else adict
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


class BaseController(SupportClass):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service_name = self.__class__.__name__

    async def get_username(self):
        raise NotImplementedError

    @property
    def has_request(self):
        return self._request is not None

    def get_bo_proxy(self):
        raise NotImplementedError

    def get_task_proxy(self, service_name):
        raise NotImplementedError

    def json(self):
        raise NotImplementedError

    def get_service_name(self) -> str:
        return self.service_name


class ObjectProxy:
    __all = None
    __services: dict = None

    def __init__(self, request, path: str = 'ecf.bo'):
        self.base_path = path
        self.request = request

    def get_object(self, service_name: str, instantiate: bool = True):
        if not instantiate:
            return self.get_service_class(service_name)
        return self.get_service_instance(service_name)

    def get_service_class(self, service_name: str):
        if not self.class_exist(service_name):
            raise ECFServiceError(f"Service [{service_name}] is not available")
        service_class = self.services.get(service_name, None)
        if not service_class:
            service_class = self.__get_package_class(service_name, self.base_path)
            self.services[service_name] = service_class
        return service_class

    @property
    def services(self):
        if self.__services is None:
            self.__services = dict()
        return self.__services

    def get_service_instance(self, service_name: str) -> object:
        service_class = self.get_service_class(service_name)
        instance = object.__new__(service_class)
        instance.__init__(self.request)
        return instance

    @property
    def all_modules(self):
        if not self.__all:
            self.__all = import_function(f"{self.base_path}:__all__")
        return self.__all

    def __get_package_class(self, class_name: str, base_path: str | None = None):
        package = f"{self.base_path if not base_path else base_path}:{class_name}"
        return import_function(package)

    def class_exist(self, klass_name: str) -> bool:
        return klass_name in self.all_modules
