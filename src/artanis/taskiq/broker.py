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
import asyncio

from taskiq import TaskiqEvents, TaskiqState
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from artanis.abc.service import StartableService
from artanis.abc.objloader import ObjectLoader
from artanis.abc.objlock import SyncLock
from artanis.abc.singleton import Singleton
from artanis.config import Configuration
from artanis.startup import artanis_startup, artanis_shutdown, artanis_monitor


class ArtanisTaskBroker(ListQueueBroker, StartableService, Singleton, SyncLock, ObjectLoader):

    def __init__(self, *args, config: Configuration = None, queue_name: str = "arttask", **kwargs):
        self.redis_url = "/".join([config.get_property_value(config.ARTANIS_REDIS_URL, None), '0'])
        super(ArtanisTaskBroker, self).__init__(self.redis_url, *args, queue_name=queue_name,**kwargs)
        for base in ArtanisTaskBroker.__bases__:
            if base is not ListQueueBroker:
                base.__init__(self, *args, **kwargs)  # type: ignore
        self.set_configuration(config)

    def do_configure(self):
        super(ArtanisTaskBroker, self).do_configure()
        config = self.get_configuration()
        self.with_result_backend(RedisAsyncResultBackend(redis_url=self.redis_url,
                                                         keep_results=False,
                                                         result_ex_time=600))

        async def internal_scheduler():
            try:
                while True:
                    await asyncio.sleep(60)
                    await artanis_monitor(config)
            except asyncio.CancelledError:
                pass

        async def process_startup(state: TaskiqState):
            loop = asyncio.get_event_loop()
            loop.create_task(internal_scheduler())
            await self.start()
            await artanis_startup(config)

        async def process_shutdown(state: TaskiqState):
            await artanis_shutdown(config)
            await self.stop()

        self.add_event_handler(TaskiqEvents.WORKER_STARTUP, process_startup)
        self.add_event_handler(TaskiqEvents.WORKER_SHUTDOWN, process_shutdown)

    def get_redis_pool(self):
        return self.connection_pool

    @classmethod
    def _configure_singleton(cls):
        cls.VM_DEFAULT.configure()

    @classmethod
    def get_default_instance(cls, *args, create_instance=True, **kwargs):
        if create_instance and not cls.has_singleton_instance():
            cls.get_class_locker().acquire()
            try:
                config = Configuration.get_default_instance()
                cls.VM_DEFAULT = object.__new__(cls)
                cls.VM_DEFAULT.__init__(*args, config=config, **kwargs)
                cls._configure_singleton()
            finally:
                cls.get_class_locker().release()
        return cls.VM_DEFAULT

class ArtanisJobBroker(ArtanisTaskBroker):

    def __init__(self, *args, config: Configuration = None, **kwargs):
        super(ArtanisJobBroker, self).__init__(*args, config=config, queue_name="artjob", **kwargs)

    def do_configure(self):
        config = self.get_configuration()
        self.with_result_backend(RedisAsyncResultBackend(redis_url=self.redis_url,
                                                         keep_results=False,
                                                         result_ex_time=600))

        async def internal_scheduler():
            try:
                while True:
                    await asyncio.sleep(60)
                    await artanis_monitor(config)
            except asyncio.CancelledError:
                pass

        async def process_startup(state: TaskiqState):
            loop = asyncio.get_event_loop()
            loop.create_task(internal_scheduler())
            await artanis_startup(config)

        async def process_shutdown(state: TaskiqState):
            await artanis_shutdown(config)

        self.add_event_handler(TaskiqEvents.WORKER_STARTUP, process_startup)
        self.add_event_handler(TaskiqEvents.WORKER_SHUTDOWN, process_shutdown)

broker = ArtanisJobBroker.get_default_instance()
task_broker = ArtanisTaskBroker.get_default_instance()

__all__ = ["broker", "task_broker"]