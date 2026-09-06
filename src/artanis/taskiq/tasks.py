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

import enum
import logging
import uuid
from functools import lru_cache
from typing import Any, Callable

from taskiq.kicker import AsyncKicker

from artanis.abc.classprops import classproperty
from artanis.asgi.auth.authentication import ArtanisUser
from artanis.config import Configuration
from artanis.events.eventexec import EventDispatcher
from artanis.taskiq.broker import batchjob_broker, task_broker, event_broker
from artanis.utils import import_function


@enum.unique
class TaskType(enum.Enum):
    TK_NONE = 0
    TK_JOB = 1
    TK_TASK = 3
    TK_EVENT = 4


@enum.unique
class JOBType(enum.Enum):
    REGULAR_JOB = 1
    LIGHT_JOB = 2


logger = logging.getLogger("artanis.task")


@event_broker.task(task_name="artanis_event")
async def artanis_event(event: dict):
    from artanis.events.eventroute import event_route
    event_type = str(event.get('event_type', ''))
    class_path = event_type.replace(".", "/")
    if not class_path.startswith("/"):
        class_path = "/" + class_path
    handler_list = event_route.get_event_handler(class_path)
    try:
        for klass, func in handler_list:
            await AsyncKicker(
                broker=event_broker,
                task_name="artanis_event_execute",
                labels={}
            ).kiq(
                klass,
                func,
                event
            )
    except Exception as e:
        logger.error(f"Failed to propagate event: {event_type}")
        logger.exception(e)


@batchjob_broker.task(task_name="artanis_task")
async def artanis_task(task_type: int, username: str, func: str, *args, **kwargs):
    request = TaskRequest(username, func, *args, **kwargs)
    return await JobHandler(request)


@task_broker.task(task_name="artanis_task")
async def artanis_task(task_type: int, username: str, func: str, *args, **kwargs):
    if task_type not in [TaskType.TK_JOB.value, TaskType.TK_TASK.value]:
        return None
    request = TaskRequest(username, func, *args, **kwargs)
    handler: type[BaseTaskHandler] = LightJobHandler if task_type == TaskType.TK_JOB else TaskHandler
    return await handler(request)


@task_broker.task(task_name="artanis_amqp")
async def artanis_amqp(queue_id: str):
    from artanis.component.queue.quexec import QueueDispatcher
    config = Configuration.get_default_instance(create_instance=False)
    await QueueDispatcher(uuid.UUID(queue_id), broker=config.container.mq_broker)


@task_broker.task(task_name="artanis_krbridge")
async def artanis_krbridge(queue_id: str):
    from artanis.component.queue.quexec import KRBDispatcher
    config = Configuration.get_default_instance(create_instance=False)
    await KRBDispatcher(uuid.UUID(queue_id), broker=config.container.mq_broker)


@event_broker.task(task_name="artanis_event_execute")
async def artanis_event_execute(klass: str, func: str, event: dict):
    await EventDispatcher.dispatch(klass, func, event)


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
    __safe_exec: Callable | None = None

    def __init__(self, request: TaskRequest):
        self.request: TaskRequest = request

    def __await__(self):
        return self.dispatch().__await__()

    async def dispatch(self):
        raise NotImplementedError

    @classmethod
    def get_service_class(cls, service_name: str):
        return import_function(service_name)

    @classmethod
    async def safe_execute(cls, func, *args, **kwargs):
        if not cls.__safe_exec:
            cls.__safe_exec = cls.get_service_class("artanis.sqlentity.entity:safe_execute")
        return await cls.__safe_exec(func, *args, **kwargs)


class IntServiceTaskHandler(BaseTaskHandler):
    __service_namespace: str = "ecf.core.intsvc:IntService"
    __service_class: Any = None

    @classmethod
    def get_service_class(cls, service_name: str = None):
        return super().get_service_class(service_name or cls.__service_namespace)

    @classproperty
    def service_class(cls):
        if not cls.__service_class:
            cls.__service_class = cls.get_service_class()
        return cls.__service_class


class CronTaskHandler(IntServiceTaskHandler):

    async def dispatch(self):
        await self.safe_execute(self.execute_cron)

    async def execute_cron(self):
        await self.service_class.proceed_cron_job(self.request)
        await self.service_class.check_unproceeded_job(self.request)


class JobHandler(IntServiceTaskHandler):
    async def dispatch(self):
        return await self.safe_execute(self.execute_job)

    async def execute_job(self):
        self.service_class.execute_job(self.request, self.request.function)


class LightJobHandler(JobHandler): ...


class TaskHandler(BaseTaskHandler):

    def __init__(self, request: TaskRequest):
        super().__init__(request)
        self.class_name, self.func_name = request.function.split('.')
        self.service_namespace = f"ecf.task.{self.class_name}:{self.class_name}"

    async def dispatch(self):
        service_instance = self.service_instance
        if not service_instance.is_configured():
            await service_instance.configure()
        func = getattr(service_instance, self.func_name)
        args, kwargs = self.request.params
        return await self.safe_execute(func, self.request, *args, **kwargs)

    @property
    def service_instance(self):
        instance = self._instantiate(self.service_namespace, self.request)
        return instance

    @lru_cache(maxsize=8)
    def _instantiate(self, service_namespace: str, request: TaskRequest):
        service_class = self.get_service_class(service_namespace)
        instance = service_class()
        instance.set_configuration(request.config)
        return instance
