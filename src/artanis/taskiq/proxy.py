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

from taskiq.kicker import AsyncKicker

from artanis.taskiq.broker import task_broker
from artanis.taskiq.tasks import TaskType


class _TaskMethod:

    def __init__(self, send: Callable, method_name: str):
        self._method_name = method_name
        self._send = send

    async def __call__(self, *args, **kwargs):
        return await self._send(self._method_name, *args, **kwargs)


class TaskObjectProxy:
    def __init__(self, username: str, service_name: str):
        self.username = username or 'ADMIN'
        self.service_name = service_name

    def __getattr__(self, func_name: str):
        return _TaskMethod(self.__submit, func_name)

    async def __submit(self, func_name: str, *args, **kwargs):
        service_func = ".".join([self.service_name, func_name])
        task = await AsyncKicker(
            broker=task_broker,
            task_name="artanis_task",
            labels={}
        ).kiq(
            TaskType.TK_TASK,
            self.username,
            service_func,
            *args,
            **kwargs
        )
        return task
