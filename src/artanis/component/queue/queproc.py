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
import abc
import logging
import typing as t
from dataclasses import is_dataclass, asdict

from pydantic import BaseModel
from redis.asyncio import Redis
from taskiq.serializers import JSONSerializer

from artanis.config import Configuration


class QueueParameters(BaseModel):
    args: list[t.Any]
    kwargs: dict[str, t.Any]


class BaseQueueProcessor(abc.ABC):

    __setname__ = "artque_processor"

    def __init__(
            self,
            queue_name: str,
            idle_timeout: float = 0.5,  # 0.5 seconds
    ):
        self.queue_name = queue_name
        self.idle_timeout = idle_timeout
        self.__connection_pool = None
        self.serializer = JSONSerializer()
        self.task_params: QueueParameters | None = None
        self.logger = logging.getLogger("artanis.streamqueue")

    @abc.abstractmethod
    async def process_queue_item(self, *args, **kwargs):
        pass

    async def finalize(self):
        """
        Finalize the processing of the queue.

        This method is called after all items in the queue have been processed.
        It can be overridden to perform any necessary cleanup or finalization tasks.
        """
        pass

    async def initialize(self):
        """
        Initialize the processing of the queue.

        This method is called before any items in the queue are processed.
        It can be overridden to perform any necessary setup or initialization tasks.
        """
        pass

    async def submit_item(self):
        if self.task_params is None:
            return
        queue_exists: bool = await self.send_task_parameters()
        if queue_exists:
            return
        await self.initialize()
        try:
            await self.launch_queue_processing_task()
        finally:
            await self.finalize()

    async def send_task_parameters(self) -> bool:
        async with Redis(connection_pool=self.connection_pool) as redis_conn:
            members = await redis_conn.smembers(self.__setname__)
            return_val = self.queue_name.encode() in members
            if not return_val:
                await redis_conn.sadd(self.__setname__, self.queue_name.encode())
            await redis_conn.lpush(
                self.queue_name,
                self.serializer.dumpb(self.task_params.model_dump(mode="json"))
            )
            return return_val

    async def launch_queue_processing_task(self):
        async with Redis(connection_pool=self.connection_pool) as redis_conn:
            try:
                while True:
                    message = await redis_conn.rpop(self.queue_name)
                    if not message:
                        break
                    task_params: QueueParameters = QueueParameters.model_validate(self.serializer.loadb(message))
                    try:
                        await self.process_queue_item(*task_params.args, **task_params.kwargs)
                    except Exception as e:
                        self.logger.error(f"Error processing queue item: {e}")
            finally:
                await redis_conn.srem(self.__setname__, self.queue_name.encode())

    @classmethod
    def _prepare_arg(cls, arg: t.Any) -> t.Any:
        if isinstance(arg, BaseModel):
            arg = arg.model_dump(mode="json")
        if is_dataclass(arg):
            if isinstance(arg, type):
                raise ValueError(
                    f"Cannot serialize types. The {arg} is not serializable.",
                )
            arg = asdict(arg)
        return arg

    def prepare_message(self, *args, **kwargs):
        self.task_params = QueueParameters(
            args=[self._prepare_arg(arg) for arg in args],
            kwargs={key: self._prepare_arg(value) for key, value in kwargs.items()},
        )

    @property
    def connection_pool(self):
        if not self.__connection_pool:
            config = Configuration.get_default_instance(create_instance=False)
            self.__connection_pool = config.container.redis_pool
        return self.__connection_pool

    def __await__(self):
        return self.submit_item().__await__()
