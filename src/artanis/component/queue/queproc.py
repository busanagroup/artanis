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
import asyncio
import logging
import time
import typing as t
from dataclasses import is_dataclass, asdict

from pydantic import BaseModel
from redis import ResponseError
from redis.asyncio import Redis
from taskiq.serializers import JSONSerializer

from artanis.config import Configuration


class QueueParameters(BaseModel):
    args: list[t.Any]
    kwargs: dict[str, t.Any]


class BaseQueueProcessor(abc.ABC):

    def __init__(
            self,
            queue_name: str,
            idle_timeout: int = 1,  # 2 seconds
    ):
        self.queue_name = queue_name
        self.idle_timeout = idle_timeout
        self.__connection_pool = None
        self.serializer = JSONSerializer()
        self.task_params: QueueParameters | None = None
        self.logger = logging.getLogger("artanis.streamqueue")
        self.semaphore = asyncio.Semaphore()

    @abc.abstractmethod
    async def process_queue_item(self, *args, **kwargs):
        pass

    async def finalize_processing(self):
        """
        Finalize the processing of the queue.

        This method is called after all items in the queue have been processed.
        It can be overridden to perform any necessary cleanup or finalization tasks.
        """
        pass

    async def submit_item(self):
        if self.task_params is None:
            return
        queue_exists: bool = await self.queue_exists()
        await self.send_task_parameters()
        if queue_exists:
            return
        # queue did not exist, launch queue processing task
        try:
            await self.launch_queue_processing_task()
        finally:
            # if the queue was created, we should delete it after processing
            await self.destroy_queue()
            await self.finalize_processing()

    async def send_task_parameters(self):
        async with Redis(connection_pool=self.connection_pool) as redis_conn:
            await redis_conn.lpush(
                self.queue_name,
                self.serializer.dumpb(self.task_params.model_dump(mode="json"))
            )

    async def get_stream_messages(self, queue: asyncio.Queue):
        async with Redis(connection_pool=self.connection_pool) as redis_conn:
            start_time = time.perf_counter()
            await self.semaphore.acquire()
            try:
                while True:
                    message = await redis_conn.brpop(self.queue_name, timeout=2)
                    if not message or not message[1]:
                        elapsed = (time.perf_counter() - start_time)
                        if elapsed > self.idle_timeout:
                            break
                    await queue.put(QueueParameters.model_validate(self.serializer.loadb(message[1])))
            finally:
                self.semaphore.release()

    async def process_queue(self, queue: asyncio.Queue):
        while True:
            if queue.empty():
                if self.semaphore.locked():
                    await asyncio.sleep(0.1)
                    continue
                else:
                    break

            task_params: QueueParameters = await queue.get()
            try:
                await self.process_queue_item(*task_params.args, **task_params.kwargs)
            except Exception as e:
                self.logger.error(f"Error processing queue item: {e}")

    async def launch_queue_processing_task(self):
        queue = asyncio.Queue()
        async with asyncio.TaskGroup() as task_group:
            task_group.create_task(self.get_stream_messages(queue))
            task_group.create_task(self.process_queue(queue))

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

    async def destroy_queue(self) -> None:
        """
        Destroy the queue.
        """
        async with Redis(connection_pool=self.connection_pool) as redis_conn:
            try:
                await redis_conn.delete(self.queue_name)
            except ResponseError as e:
                pass

    async def queue_exists(self) -> bool:
        """
        Check if the queue exists.
        """
        return_val: bool = False
        async with Redis(connection_pool=self.connection_pool) as redis_conn:
            try:
                key_exists = await redis_conn.exists(self.queue_name)
                return_val = True if key_exists else False
            except ResponseError as e:
                return_val = False
        return return_val

    @property
    def connection_pool(self):
        if not self.__connection_pool:
            config = Configuration.get_default_instance(create_instance=False)
            self.__connection_pool = config.container.redis_pool
        return self.__connection_pool

    def __await__(self):
        return self.submit_item().__await__()
