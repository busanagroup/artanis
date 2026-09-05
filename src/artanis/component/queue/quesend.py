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
import typing as t
import uuid

from taskiq.kicker import AsyncKicker

from artanis.component.queue.types import QueueType
from artanis.config import Configuration
from artanis.taskiq.broker import task_broker
from artanis.utils import import_function


class QueueSubmitter:
    __safe_exec: t.Callable | None = None
    __get_entity: t.Callable | None = None

    def __init__(self, exchange: str, route_key: str, message: bytes, execute_immediately: bool = True):
        self.config = Configuration.get_default_instance(create_instance=False)
        self.entity = None
        self.exchange = exchange
        self.route_key = route_key
        self.message = message
        self.execute_immediately = execute_immediately

    def get_task_name(self) -> str:
        return "artanis_amqp"

    def get_queue_type(self) -> int:
        return QueueType.CLOUD_EVENT.value

    async def submit_queue_item(self):
        if not self.entity:
            self.entity = self.get_entity('efmque')
        queue_id: uuid.UUID = await self.entity.queue_add(self.exchange, self.route_key, self.message, que_type=self.get_queue_type())
        if not self.execute_immediately:
            return
        await AsyncKicker(
            broker=task_broker,
            task_name=self.get_task_name(),
            labels={}
        ).kiq(str(queue_id))

    @classmethod
    def get_service_class(cls, service_name: str):
        return import_function(service_name)

    @classmethod
    async def safe_execute(cls, func, *args, **kwargs):
        if not cls.__safe_exec:
            cls.__safe_exec = cls.get_service_class("artanis.sqlentity.entity:safe_execute")
        return await cls.__safe_exec(func, *args, **kwargs)

    @classmethod
    def get_entity(cls, entity_id: str):
        if not cls.__get_entity:
            cls.__get_entity = cls.get_service_class("artanis.sqlentity.entity:get_entity")
        return cls.__get_entity(entity_id)

    def __await__(self):
        return self.submit_queue_item().__await__()

