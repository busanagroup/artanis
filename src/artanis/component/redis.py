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
import socket

from redis import Redis as SyncRedisPy, ConnectionPool as SyncConnectionPool
from redis.asyncio import Redis as AsyncRedisPy, ConnectionPool as AsyncConnectionPool

from artanis.abc.objlock import SyncLock, AsyncLock
from artanis.abc.singleton import Singleton, AsyncSingleton
from artanis.config import Configuration


class Redis(SyncRedisPy, Singleton, SyncLock):
    def __init__(
            self,
            config: Configuration = None,
            connection_pool: AsyncConnectionPool = None,
            single_connection_client: bool = False,
    ):
        config = config or Configuration().get_default_instance(create_instance=False)
        ka_options = {
            socket.TCP_KEEPIDLE: 10,
            socket.TCP_KEEPINTVL: 5,
            socket.TCP_KEEPCNT: 5
        }
        redis_url = config.get_property_value(config.ARTANIS_REDIS_URL)
        connection_pool = connection_pool or config.container.redis_pool \
            if hasattr(config.container, "redis_pool") else \
            AsyncConnectionPool.from_url(redis_url,
                                         health_check_interval=10,
                                         socket_connect_timeout=5,
                                         retry_on_timeout=True,
                                         socket_keepalive=True,
                                         socket_keepalive_options=ka_options,
                                         max_connections=16,
                                         )
        super().__init__(connection_pool=connection_pool,
                         single_connection_client=single_connection_client,
                         health_check_interval=10,
                         socket_connect_timeout=5,
                         retry_on_timeout=True,
                         socket_keepalive=True,
                         max_connections=16,
                         )
        self.auto_close_connection_pool = False

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
    def __init__(
            self,
            config: Configuration = None,
            connection_pool: AsyncConnectionPool = None,
            single_connection_client: bool = False,
    ):
        config = config or Configuration().get_default_instance(create_instance=False)
        redis_url = config.get_property_value(config.ARTANIS_REDIS_URL)
        ka_options = {
            socket.TCP_KEEPIDLE: 10,
            socket.TCP_KEEPINTVL: 5,
            socket.TCP_KEEPCNT: 5
        }
        connection_pool = connection_pool or config.container.redis_pool \
            if hasattr(config.container, "redis_pool") else \
            AsyncConnectionPool.from_url(redis_url,
                                         health_check_interval=10,
                                         socket_connect_timeout=5,
                                         retry_on_timeout=True,
                                         socket_keepalive=True,
                                         socket_keepalive_options=ka_options,
                                         max_connections=16,
                                         )
        super().__init__(connection_pool=connection_pool,
                         single_connection_client=single_connection_client,
                         health_check_interval=10,
                         socket_connect_timeout=5,
                         retry_on_timeout=True,
                         socket_keepalive=True,
                         max_connections=16,
                         )
        self.auto_close_connection_pool = False

    @classmethod
    async def get_default_instance(cls, *args, create_instance=True, **kwargs):
        await cls.get_class_locker().acquire()
        try:
            if create_instance and not cls.has_singleton_instance():
                cls.VM_DEFAULT = cls(*args, **kwargs)
            return cls.VM_DEFAULT
        finally:
            cls.get_class_locker().release()
