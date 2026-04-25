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


import enum
import logging
from typing import Any, Callable

from artanis.abc.classprops import classproperty
from artanis.asgi.auth.authentication import ArtanisUser
from artanis.config import Configuration
from artanis.taskiq.broker import broker, task_broker
from artanis.utils import import_function


@enum.unique
class TaskType(enum.Enum):
    TK_NONE = 0
    TK_JOB = 1
    TK_TASK = 2


@enum.unique
class JOBType(enum.Enum):
    REGULAR_JOB = 1
    LIGHT_JOB = 2


logger = logging.getLogger("artanis.task")


@broker.task(task_name="artanis_task")
async def artanis_task(task_type: int, username: str, func: str, *args, **kwargs):
    request = TaskRequest(username, func, *args, **kwargs)
    return await JobTaskHandler(request)


@task_broker.task(task_name="artanis_task")
async def artanis_task(task_type: int, username: str, func: str, *args, **kwargs):
    handler = None if task_type == TaskType.TK_NONE else \
        JobTaskHandler if task_type == 1 else LightTaskHandler
    if not handler:
        return None
    request = TaskRequest(username, func, *args, **kwargs)
    return await handler(request)


@task_broker.task(task_name="artanis_schedule")
async def artanis_schedule(*args, **kwargs):
    return await CronTaskHandler(TaskRequest("SYSTEM", None))


class TaskRequest:

    def __init__(self, username: str, func: str, *args, **kwargs):
        self._cookies = {'user': ArtanisUser(username)}
        self._config = Configuration.get_default_instance(create_instance=False)
        self._function = func
        self._params = [args, kwargs]

    @property
    def user(self) -> Any:
        return self._cookies["user"]

    @property
    def config(self) -> Configuration:
        return self._config

    @property
    def function(self) -> Any:
        return self._function

    @property
    def params(self):
        return self._params


class BaseTaskHandler:
    __service_instance = None
    __safe_exec: Callable | None = None
    __class_registry: dict = dict()

    def __init__(self, request: TaskRequest):
        self.request = request

    def __await__(self):
        return self.dispatch().__await__()

    async def dispatch(self):
        raise NotImplementedError

    @classmethod
    async def safe_execute(cls, func, *args, **kwargs):
        if not cls.__safe_exec:
            cls.__safe_exec = import_function("artanis.sqlentity.entity:safe_execute")
        return await cls.__safe_exec(func, *args, **kwargs)

    def get_object(self, instantiate: bool = True):
        if not instantiate:
            return self.service_class
        return self.service_instance

    @classproperty
    def service_class(cls):
        return cls.get_service_class("ecf.core.intsvc:IntService")

    @classmethod
    def get_service_class(cls, service_name: str):
        service_class = cls.__class_registry.get(service_name)
        if not service_class:
            service_class = import_function(service_name)
            cls.__class_registry[service_name] = service_class
        return service_class

    @property
    def service_instance(self):
        if not self.__service_instance:
            service_class = self.service_class
            self.__service_instance = object.__new__(service_class)
            self.__service_instance.__init__(self.request)
        return self.__service_instance


class CronTaskHandler(BaseTaskHandler):

    async def dispatch(self):
        await self.safe_execute(self.execute_cron)

    async def execute_cron(self):
        await self.service_instance.proceed_cron_job()
        await self.service_instance.check_unproceeded_job()


class JobTaskHandler(BaseTaskHandler):

    async def dispatch(self):
        return await self.safe_execute(self.service_class.execute_job, self.request, self.request.function)


class LightTaskHandler(BaseTaskHandler):

    def __init__(self, request: TaskRequest):
        super().__init__(request)
        self._class_name, self._func_name = request.function.split('.')

    async def dispatch(self):
        func = getattr(self._func_name, self.service_instance)
        args, kwargs = self.request.params
        return await self.safe_execute(func, *args, **kwargs)

    @property
    def service_instance(self):
        if not self.__service_instance:
            service_name = f"ecf.task.{self._class_name}:{self._class_name}"
            service_class = self.get_service_class(service_name)
            self.__service_instance = object.__new__(service_class)
            self.__service_instance.__init__(self.request)
        return self.__service_instance
