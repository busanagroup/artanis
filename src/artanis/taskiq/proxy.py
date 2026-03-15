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

from typing import Callable, Any

from taskiq.kicker import AsyncKicker

from artanis.taskiq.broker import broker, task_broker
from artanis.taskiq.tasks import TaskType, JOBType


class _TaskMethod:

    def __init__(self, send: Callable, method_name: str):
        self._method_name = method_name
        self._send = send

    async def __call__(self, *args, **kwargs):
        return await self._send(self._method_name, *args, **kwargs)


class AbstractJobObjectProxy(object):
    def __init__(self, request: Any):
        self.request = request

    async def get_username(self):
        if not self.request:
            return None
        if hasattr(self.request, 'user'):
            user_name = self.request.user.username
        else:
            user_name = self.request.user_name
        return user_name


class TaskObjectProxy(AbstractJobObjectProxy):
    def __init__(self, request, service_name: str):
        super().__init__(request)
        self.service_name = service_name

    def __getattr__(self, func_name: str):
        return _TaskMethod(self.__request, func_name)

    async def __request(self, func_name: str, *args, **kwargs):
        service_func = ".".join([self.service_name, func_name])
        request = self.request
        await AsyncKicker(broker=task_broker, task_name="artanis_task",
                          labels={}).kiq(TaskType.TK_TASK, request.user.username,
                                         service_func, *args, **kwargs)


class JobObjectProxy(AbstractJobObjectProxy):

    def __init__(self, request: Any, job_service: str, job_id: str):
        super().__init__(request)
        self.job_id = job_id
        self.job_service = job_service

    def __await__(self):
        return self.dispatch().__await__()

    async def dispatch(self):
        job_channel = broker if self.get_task_type() == JOBType.REGULAR_JOB else task_broker
        await AsyncKicker(broker=job_channel,
                          task_name="artanis_task",
                          labels={}).kiq(TaskType.TK_JOB,
                                         self.get_username(),
                                         self.job_id)

    def get_task_type(self):
        raise NotImplementedError()  # pragma: no cover
