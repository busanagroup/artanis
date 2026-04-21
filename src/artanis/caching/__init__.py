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
import functools
import inspect
from contextlib import AbstractContextManager
from typing import Callable, Any, Optional, MutableMapping

from artanis.caching.base import (hashkey, methodkey, typedkey, typedmethodkey,
                                  _KT, _T, IdentityFunction, NullContext)
from artanis.caching.cache import TTLCache, LRUCache, TLRUCache
from artanis.caching.redisttl import RedisCache

__all__ = ['cached', 'cachedfunction', 'cachedmethod', 'hashkey', 'methodkey', 'typedkey', 'typedmethodkey',
           'LRUCache', 'TTLCache', 'TLRUCache', 'RedisCache']



def cached(
        cache: Callable[[Any], Optional[MutableMapping[_KT, Any]]] | Optional[MutableMapping[_KT, Any]] = None,
        key: Callable[..., _KT] = hashkey,
        lock: Optional[Callable[[Any], "AbstractContextManager[Any]"]] = None,
) -> IdentityFunction:
    """
    Decorator to automatically wrap a function or methodwith a memoizing callable
    that saves results in a cache.

    When ``lock`` is provided for a standard function, it's expected to
    implement ``__enter__`` and ``__exit__`` that will be used to lock
    the cache when gets updated. If it wraps a coroutine, ``lock``
    must implement ``__aenter__`` and ``__aexit__``.
    """
    lock = lock or NullContext()
    cache = cache or TTLCache(8, 300)

    def decorator(func):
        if inspect.ismethod(func):
            if inspect.iscoroutinefunction(func):
                async def wrapper(self, *args, **kwargs):
                    _cached = bool(kwargs.pop('_cached')) if '_cached' in kwargs else True
                    if not _cached:
                        return await func(self, *args, **kwargs)
                    method_cache = cache(self)
                    if method_cache is None:
                        return await func(self, *args, **kwargs)
                    k = key(self, *args, **kwargs)
                    try:
                        async with lock(self):
                            return method_cache[k]
                    except KeyError:
                        pass  # key not found
                    val = await func(self, *args, **kwargs)
                    try:
                        async with lock(self):
                            method_cache[k] = val
                    except ValueError:
                        pass  # val too large
                    return val
            else:
                def wrapper(self, *args, **kwargs):
                    _cached = bool(kwargs.pop('_cached')) if '_cached' in kwargs else True
                    if not _cached:
                        return func(self, *args, **kwargs)
                    method_cache = cache(self)
                    if method_cache is None:
                        return func(self, *args, **kwargs)
                    k = key(*args, **kwargs)
                    try:
                        with lock(self):
                            return method_cache[k]
                    except KeyError:
                        pass  # key not found
                    val = func(self, *args, **kwargs)
                    try:
                        with lock(self):
                            method_cache[k] = val
                    except ValueError:
                        pass  # val too large
                    return val
        else:
            if inspect.iscoroutinefunction(func):
                async def wrapper(*args, **kwargs):
                    _cached = bool(kwargs.pop('_cached')) if '_cached' in kwargs else True
                    if not _cached:
                        return await func(*args, **kwargs)
                    k = key(*args, **kwargs)
                    try:
                        async with lock:
                            return cache[k]
                    except KeyError:
                        pass  # key not found
                    val = await func(*args, **kwargs)
                    try:
                        async with lock:
                            cache[k] = val
                    except ValueError:
                        pass  # val too large
                    return val
            else:
                def wrapper(*args, **kwargs):
                    _cached = bool(kwargs.pop('_cached')) if '_cached' in kwargs else True
                    if not _cached:
                        return func(*args, **kwargs)
                    k = key(*args, **kwargs)
                    try:
                        with lock:
                            return cache[k]
                    except KeyError:
                        pass  # key not found
                    val = func(*args, **kwargs)
                    try:
                        with lock:
                            cache[k] = val
                    except ValueError:
                        pass  # val too large
                    return val
        return functools.wraps(func)(wrapper)

    return decorator


def cachedfunction(
        cache: Optional[MutableMapping[_KT, Any]] = None,
        key: Callable[..., _KT] = hashkey,  # type:ignore
        lock: Optional[AbstractContextManager[Any]] = None,
) -> IdentityFunction:
    """
    Decorator to wrap a function or a coroutine with a memoizing callable
    that saves results in a cache.

    When ``lock`` is provided for a standard function, it's expected to
    implement ``__enter__`` and ``__exit__`` that will be used to lock
    the cache when gets updated. If it wraps a coroutine, ``lock``
    must implement ``__aenter__`` and ``__aexit__``.
    """
    lock = lock or NullContext()
    cache = cache or TTLCache(8, 300)

    def decorator(func):
        if inspect.iscoroutinefunction(func):
            async def wrapper(*args, **kwargs):
                k = key(*args, **kwargs)
                try:
                    async with lock:
                        return cache[k]
                except KeyError:
                    pass  # key not found

                val = await func(*args, **kwargs)
                try:
                    async with lock:
                        cache[k] = val
                except ValueError:
                    pass  # val too large

                return val
        else:
            def wrapper(*args, **kwargs):
                k = key(*args, **kwargs)
                try:
                    with lock:
                        return cache[k]
                except KeyError:
                    pass  # key not found

                val = func(*args, **kwargs)
                try:
                    with lock:
                        cache[k] = val
                except ValueError:
                    pass  # val too large

                return val

        return functools.wraps(func)(wrapper)

    return decorator


def cachedmethod(
        cache: Callable[[Any], Optional[MutableMapping[_KT, Any]]],
        key: Callable[..., _KT] = hashkey,  # type:ignore
        lock: Optional[Callable[[Any], "AbstractContextManager[Any]"]] = None,
) -> IdentityFunction:
    """Decorator to wrap a class or instance method with a memoizing
    callable that saves results in a cache. This works similarly to
    `cached`, but the arguments `cache` and `lock` are callables that
    return the cache object and the lock respectively.
    """
    lock = lock or (lambda _: NullContext())
    cache = cache or TTLCache(8, 300)

    def decorator(method):
        if inspect.iscoroutinefunction(method):
            async def wrapper(self, *args, **kwargs):
                method_cache = cache(self)
                if method_cache is None:
                    return await method(self, *args, **kwargs)

                k = key(self, *args, **kwargs)
                try:
                    async with lock(self):
                        return method_cache[k]
                except KeyError:
                    pass  # key not found

                val = await method(self, *args, **kwargs)
                try:
                    async with lock(self):
                        method_cache[k] = val
                except ValueError:
                    pass  # val too large

                return val
        else:
            def wrapper(self, *args, **kwargs):
                method_cache = cache(self)
                if method_cache is None:
                    return method(self, *args, **kwargs)

                k = key(*args, **kwargs)
                try:
                    with lock(self):
                        return method_cache[k]
                except KeyError:
                    pass  # key not found

                val = method(self, *args, **kwargs)
                try:
                    with lock(self):
                        method_cache[k] = val
                except ValueError:
                    pass  # val too large

                return val
        return functools.wraps(method)(wrapper)

    return decorator
