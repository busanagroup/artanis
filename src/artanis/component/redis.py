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


from redis import Redis as SyncRedisPy, ConnectionPool as SyncConnectionPool
from redis.asyncio import Redis as AsyncRedisPy, ConnectionPool as AsyncConnectionPool

from artanis.abc.objlock import SyncLock, AsyncLock
from artanis.abc.singleton import Singleton, AsyncSingleton
from artanis.config import Configuration


class Redis(SyncRedisPy, Singleton, SyncLock):
    def __init__(self, config: Configuration = None):
        config = config or Configuration().get_default_instance(create_instance=False)
        redis_url = config.get_property_value(config.ARTANIS_REDIS_URL)
        connection_pool = config.container.redis_pool \
            if hasattr(config.container, "redis_pool") else \
            AsyncConnectionPool.from_url(redis_url)
        super().__init__(connection_pool=connection_pool,
                         single_connection_client=False)
        self.auto_close_connection_pool = True

    @classmethod
    def get_default_instance(cls, *args, create_instance=False, **kwargs):
        cls.get_class_locker().acquire()
        try:
            if create_instance and not cls.has_singleton_instance():
                cls.VM_DEFAULT = cls(*args, **kwargs)
            return cls.VM_DEFAULT
        finally:
            cls.get_class_locker().release()


class AsyncRedis(AsyncRedisPy, AsyncSingleton, AsyncLock):
    def __init__(self, config: Configuration = None):
        config = config or Configuration().get_default_instance(create_instance=False)
        redis_url = config.get_property_value(config.ARTANIS_REDIS_URL)
        connection_pool = config.container.redis_pool \
            if hasattr(config.container, "redis_pool") else \
            AsyncConnectionPool.from_url(redis_url)
        super().__init__(connection_pool=connection_pool,
                         single_connection_client=False)
        self.auto_close_connection_pool = True

    @classmethod
    async def get_default_instance(cls, *args, create_instance=True, **kwargs):
        await cls.get_class_locker().acquire()
        try:
            if create_instance and not cls.has_singleton_instance():
                cls.VM_DEFAULT = cls(*args, **kwargs)
            return cls.VM_DEFAULT
        finally:
            cls.get_class_locker().release()
