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
import functools
import inspect
import pickle
import typing as t

from artanis.caching import hashkey, _KT, _T, NullContext
from artanis.config import Configuration

if t.TYPE_CHECKING:
    from artanis.component.redis import AsyncRedis, Redis as SyncRedis


class RedisCache:

    def __init__(
            self,
            namespace: str,
            ttl: int=1800, # 30 minutes cached
            cache_enforce: bool=True,
    ):
        self.config = Configuration.get_default_instance(create_instance=False)
        self.__async_redis: AsyncRedis = None
        self.__sync_redis: SyncRedis = None
        self.__namespace = namespace
        self.__ttl = ttl
        self.__cache_enforce = cache_enforce

    @property
    def async_redis(self) -> AsyncRedis:
        if not self.__async_redis:
            self.__async_redis = self.config.container.async_redis
        return self.__async_redis

    @property
    def sync_redis(self) -> SyncRedis:
        if not self.__sync_redis:
            self.__sync_redis = self.config.container.sync_redis
        return self.__sync_redis

    def cached(
            self,
            ttl: int | None = None,
            key: t.Callable[..., _KT] = hashkey
    ):
        lock = NullContext()
        def decorator(func):
            if inspect.iscoroutinefunction(func):
                async def wrapper(sself, *args, **kwargs):
                    _cached = bool(kwargs.pop('_cached')) if '_cached' in kwargs else self.__cache_enforce
                    if not _cached:
                        return await func(sself, *args, **kwargs)
                    key_parts = [self.__namespace, func.__name__, *args, *(kwargs.values())]
                    _key = ":".join(str(k).replace(" ", "") for k in key_parts)
                    _ttl = ttl or self.__ttl
                    client = self.async_redis.client()
                    async with client:
                        try:
                            async with lock:
                                val = await client.get(_key)
                            if not val:
                                raise KeyError()
                            return RedisCache.deserialize(val)
                        except (KeyError, Exception):
                            pass
                        val = await func(sself, *args, **kwargs)
                        try:
                            async with lock:
                                await client.setex(_key, _ttl, RedisCache.serialize(val))
                        except (ValueError, Exception):
                            pass
                    return val
            else:
                def wrapper(sself, *args, **kwargs):
                    _cached = bool(kwargs.pop('_cached')) if '_cached' in kwargs else self.__cache_enforce
                    if not _cached:
                        return func(sself, *args, **kwargs)
                    key_parts = [self.__namespace, func.__name__, *args, *(kwargs.values())]
                    _key = ":".join(str(k).replace(" ", "") for k in key_parts)
                    _ttl = ttl or self.__ttl
                    client = self.sync_redis.client()
                    with client:
                        try:
                            with lock:
                                val = client.get(_key)
                            if not val:
                                raise KeyError()
                            return RedisCache.deserialize(val)
                        except KeyError:
                            pass
                        val = func(sself, *args, **kwargs)
                        try:
                            with lock:
                                client.setex(_key, _ttl, RedisCache.serialize(val))
                        except ValueError:
                            pass
                    return val
            return functools.wraps(func)(wrapper)
        return decorator

    @staticmethod
    def deserialize(value):
        return pickle.loads(value)

    @staticmethod
    def serialize(value):
        return pickle.dumps(value)















