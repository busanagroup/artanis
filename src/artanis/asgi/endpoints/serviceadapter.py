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
from typing import Callable, Any

from artanis.asgi.http import Request
from artanis.sqlentity import safe_execute


class ServiceAdapter:

    def __init__(self, request: Request, base_path: str):
        self.base_path: str = base_path
        self.request: Request = request
        self.__service_class = request.scope['module_class']
        self.__service_instance = None

    def get_object(self, instantiate: bool = True):
        if not instantiate:
            return self.__service_class
        return self.service_instance

    def get_class_name(self):
        return self.__service_class.__name__

    @property
    def service_instance(self):
        if not self.__service_instance:
            service_class = self.__service_class
            self.__service_instance = service_class(self.request)
        return self.__service_instance

    @staticmethod
    async def safe_execute(func: Callable[..., Any], *args, **kwargs):
        return safe_execute(func, *args, **kwargs)
