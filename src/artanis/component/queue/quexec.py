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

import asyncio
import logging
import typing as t
import uuid

from faststream.rabbit import RabbitBroker, RabbitExchange, ExchangeType

from artanis.component.queue.types import QueueType
from artanis.config import Configuration
from artanis.utils import import_function

logger = logging.getLogger(__name__)


class BaseQueueDispatcher:
    __safe_exec: t.Callable | None = None
    __get_entity: t.Callable | None = None
    __exchange_type: ExchangeType | None = None
    __dispatched: bool | None = None

    def __init__(self, queue_id: uuid.UUID, broker: RabbitBroker, delay_every: int = 100):
        self.queue = asyncio.Queue()
        self.queue_id: uuid.UUID = queue_id
        self.queue.put_nowait(self.queue_id)
        self.config = Configuration.get_default_instance(create_instance=False)
        self.entity = None
        self.delay_every: int = delay_every
        self.broker: RabbitBroker = broker
        self.exchange_name: str | None = None
        self.queue_exchange: RabbitExchange | None = None

    async def dispatch(self):
        if self.__class__.__dispatched:
            return
        self.__class__.__dispatched = True
        try:
            await self.dispatch_queue(mode=1)
            while True:
                if not await self.dispatch_queue(mode=0):
                    break
                await asyncio.sleep(0.1)
        finally:
            self.__class__.__dispatched = False
            if self.broker._connection is not None:
                await self.broker.stop()

    async def dispatch_queue(self, mode: int = 0) -> bool:
        queue_list = await self.get_list(status=0 if mode == 0 else 9)
        for item in queue_list:
            self.queue.put_nowait(item)
        if self.queue.empty():
            return False
        try:
            dispatched_total: int = 0
            while not self.queue.empty():
                queue_id = await self.queue.get()
                await self.dispatch_item(queue_id)
                dispatched_total += 1
                if dispatched_total % self.delay_every == 0:
                    await asyncio.sleep(0.1)
            return True
        except Exception as ex:
            logger.error(f"Error dispatching queue: {ex}")
            logger.exception(ex)
        return False

    async def get_list(self, status: int = 0) -> list[uuid.UUID]:
        if not self.entity:
            self.entity = self.get_entity('efmque')
        return await self.entity.queue_get_except(self.queue_id, que_type=QueueType.CLOUD_EVENT.value, status=status)

    async def dispatch_item(self, queue_id: uuid.UUID):
        if not self.entity:
            self.entity = self.get_entity('efmque')
        queue_item = await self.entity.get_or_none(mquepkid=queue_id)
        if not queue_item or queue_item.mquestat not in [0, 9]:
            return
        try:
            await self.entity.queue_update_status(queue_id, status=1)
            if self.broker._connection is None:
                await self.broker.connect()
            if self.exchange_name != queue_item.mquexchg:
                self.exchange_name = queue_item.mquexchg
                self.queue_exchange = RabbitExchange(
                    name=self.exchange_name,
                    type=self.__exchange_type
                )
                await self.broker.declare_exchange(self.queue_exchange)
            if queue_item.mquerout:
                await self.broker.publish(
                    queue_item.mquedata,
                    exchange=self.queue_exchange,
                    routing_key=queue_item.mquerout
                )
            else:
                await self.broker.publish(
                    queue_item.mquedata,
                    exchange=self.queue_exchange,
                )
            await self.entity.queue_delete(queue_id)
        except Exception as ex:
            await self.entity.queue_update_status(queue_id, status=9)
            logger.error("Error dispatching queue item %s", queue_id)
            logger.exception(ex)

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
        return self.dispatch().__await__()


class QueueDispatcher(BaseQueueDispatcher):
    __exchange_type: ExchangeType = ExchangeType.TOPIC
    __dispatched = False


class KRBDispatcher(BaseQueueDispatcher):
    __exchange_type: ExchangeType = ExchangeType.FANOUT
    __dispatched = False

    async def get_list(self, status: int = 0) -> list[uuid.UUID]:
        if not self.entity:
            self.entity = self.get_entity('efmque')
        return await self.entity.queue_get_except(self.queue_id, que_type=QueueType.KR_BRIDGE.value, status=status)

    async def dispatch_item(self, queue_id: uuid.UUID):
        if not self.entity:
            self.entity = self.get_entity('efmque')
        queue_item = await self.entity.get_or_none(mquepkid=queue_id)
        if not queue_item or queue_item.mquestat != 0:
            return
        try:
            await self.entity.queue_update_status(queue_id, status=1)
            if self.broker._connection is None:
                await self.broker.connect()
            if self.exchange_name != queue_item.mquexchg:
                self.exchange_name = queue_item.mquexchg
                self.queue_exchange = RabbitExchange(
                    name=self.exchange_name,
                    type=self.__exchange_type,
                    durable=True,
                    auto_delete=True
                )
                await self.broker.declare_exchange(self.queue_exchange)
            await self.broker.publish(queue_item.mquedata, exchange=self.queue_exchange)
            await self.entity.queue_delete(queue_id)
        except Exception as ex:
            await self.entity.queue_update_status(queue_id, status=9)
            logger.error("Error dispatching KRB queue item %s", queue_id)
            logger.exception(ex)
