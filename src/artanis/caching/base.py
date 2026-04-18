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
import collections
import functools
from time import monotonic


class DefaultSize:
    """A minimal "fake" dict that returns a constant size 1 for any key."""

    __slots__ = ()

    def __getitem__(self, _key):
        return 1

    def __setitem__(self, _key, _value): ...

    def pop(self, _key):
        return 1

    def clear(self): ...


class Cache(collections.abc.MutableMapping):
    """Mutable mapping to serve as a simple cache or cache base class."""

    __marker = object()

    __size = DefaultSize()

    def __init__(self, maxsize, getsizeof=None):
        if getsizeof:
            self.getsizeof = getsizeof
        if self.getsizeof is not Cache.getsizeof:
            self.__size = dict()
        self.__data = dict()
        self.__currsize = 0
        self.__maxsize = maxsize

    def __repr__(self):
        return "%s(%s, maxsize=%r, currsize=%r)" % (
            type(self).__name__,
            repr(self.__data),
            self.__maxsize,
            self.__currsize,
        )

    def __getitem__(self, key):
        try:
            return self.__data[key]
        except KeyError:
            return self.__missing__(key)

    def __setitem__(self, key, value):
        maxsize = self.__maxsize
        size = self.getsizeof(value)
        if size > maxsize:
            raise ValueError("value too large")
        if key not in self.__data or self.__size[key] < size:
            while self.__currsize + size > maxsize:
                self.popitem()
        if key in self.__data:
            diffsize = size - self.__size[key]
        else:
            diffsize = size
        self.__data[key] = value
        self.__size[key] = size
        self.__currsize += diffsize

    def __delitem__(self, key):
        size = self.__size.pop(key)
        del self.__data[key]
        self.__currsize -= size

    def __contains__(self, key):
        return key in self.__data

    def __missing__(self, key):
        raise KeyError(key)

    def __iter__(self):
        return iter(self.__data)

    def __len__(self):
        return len(self.__data)

    def get(self, key, default=None):
        if key in self:
            return self[key]
        else:
            return default

    def pop(self, key, default=__marker):
        if key in self:
            value = self[key]
            del self[key]
        elif default is self.__marker:
            raise KeyError(key)
        else:
            value = default
        return value

    def setdefault(self, key, default=None):
        if key in self:
            value = self[key]
        else:
            self[key] = value = default
        return value

    def clear(self):
        self.__data.clear()
        self.__size.clear()
        self.__currsize = 0

    @property
    def maxsize(self):
        return self.__maxsize

    @property
    def currsize(self):
        return self.__currsize

    @staticmethod
    def getsizeof(value):
        return 1


class TimedCache(Cache):
    """Base class for time aware cache implementations."""

    class Timer:
        def __init__(self, timer):
            self.__timer = timer
            self.__nesting = 0

        def __call__(self):
            if self.__nesting == 0:
                return self.__timer()
            else:
                return self.__time

        def __enter__(self):
            if self.__nesting == 0:
                self.__time = _time = self.__timer()
            else:
                _time = self.__time
            self.__nesting += 1
            return _time

        def __exit__(self, *exc):
            self.__nesting -= 1

        def __reduce__(self):
            return TimedCache.Timer, (self.__timer,)

        def __getattr__(self, name):
            return getattr(self.__timer, name)

    def __init__(self, maxsize, timer=monotonic, getsizeof=None):
        Cache.__init__(self, maxsize, getsizeof)
        self.__timer = TimedCache.Timer(timer)

    def __repr__(self, cache_repr=Cache.__repr__):
        with self.__timer as _time:
            self.expire(_time)
            return cache_repr(self)

    def __len__(self, cache_len=Cache.__len__):
        with self.__timer as _time:
            self.expire(_time)
            return cache_len(self)

    @property
    def currsize(self):
        with self.__timer as _time:
            self.expire(_time)
            return super().currsize

    @property
    def timer(self):
        """The timer function used by the cache."""
        return self.__timer

    def get(self, *args, **kwargs):
        with self.__timer:
            return super().get(*args, **kwargs)

    def pop(self, *args, **kwargs):
        with self.__timer:
            return super().pop(*args, **kwargs)

    def setdefault(self, *args, **kwargs):
        with self.__timer:
            return super().setdefault(*args, **kwargs)

    def clear(self):
        super().clear()


class HashedTuple(tuple):
    """A tuple that ensures that hash() will be called no more than once
    per element, since cache decorators will hash the key multiple
    times on a cache miss.  See also _HashedSeq in the standard
    library functools implementation.

    """

    __hashvalue = None  # default value, set in instance on first use

    def __hash__(self, hash=tuple.__hash__):
        hashvalue = self.__hashvalue
        if hashvalue is None:
            self.__hashvalue = hashvalue = hash(self)
        return hashvalue

    def __add__(self, other, add=tuple.__add__):
        return HashedTuple(add(self, other))

    def __radd__(self, other, add=tuple.__add__):
        return HashedTuple(add(other, self))

    def __getstate__(self):
        return {}


# A sentinel for separating args from kwargs.  Using the class itself
# ensures uniqueness and preserves identity when pickling/unpickling.
kwmark = (HashedTuple,)


def hashkey(*args, **kwargs):
    """Return a cache key for the specified hashable arguments."""

    if kwargs:
        return HashedTuple(args + kwmark + tuple(sorted(kwargs.items())))
    else:
        return HashedTuple(args)


def methodkey(self, *args, **kwargs):
    """Return a cache key for use with cached methods."""
    return hashkey(*args, **kwargs)


def typedkey(*args, **kwargs):
    """Return a typed cache key for the specified hashable arguments."""

    if kwargs:
        sorted_kwargs = tuple(sorted(kwargs.items()))
        key = HashedTuple(args + kwmark + sorted_kwargs)
        key += tuple(type(v) for _, v in sorted_kwargs)
    else:
        key = HashedTuple(args)
    key += tuple(type(v) for v in args)
    return key


def typedmethodkey(self, *args, **kwargs):
    """Return a typed cache key for use with cached methods."""
    return typedkey(*args, **kwargs)


def uncached_info(func, info):
    misses = 0

    def wrapper(*args, **kwargs):
        nonlocal misses
        misses += 1
        return func(*args, **kwargs)

    def cache_clear():
        nonlocal misses
        misses = 0

    wrapper.cache_clear = cache_clear
    wrapper.cache_info = lambda: info(0, misses)
    return wrapper


def condition_info(func, cache, key, lock, cond, info):
    hits = misses = 0
    pending = set()

    def wrapper(*args, **kwargs):
        nonlocal hits, misses
        k = key(*args, **kwargs)
        with lock:
            cond.wait_for(lambda: k not in pending)
            try:
                result = cache[k]
                hits += 1
                return result
            except KeyError:
                pending.add(k)
                misses += 1
        try:
            v = func(*args, **kwargs)
            with lock:
                try:
                    cache[k] = v
                except ValueError:
                    pass  # value too large
                return v
        finally:
            with lock:
                pending.remove(k)
                cond.notify_all()

    def cache_clear():
        nonlocal hits, misses
        with lock:
            cache.clear()
            hits = misses = 0

    def cache_info():
        with lock:
            return info(hits, misses)

    wrapper.cache_clear = cache_clear
    wrapper.cache_info = cache_info
    return wrapper


def locked_info(func, cache, key, lock, info):
    hits = misses = 0

    def wrapper(*args, **kwargs):
        nonlocal hits, misses
        k = key(*args, **kwargs)
        with lock:
            try:
                result = cache[k]
                hits += 1
                return result
            except KeyError:
                misses += 1
        v = func(*args, **kwargs)
        with lock:
            try:
                # In case of a race condition, i.e. if another thread
                # stored a value for this key while we were calling
                # func(), prefer the cached value.
                return cache.setdefault(k, v)
            except ValueError:
                return v  # value too large

    def cache_clear():
        nonlocal hits, misses
        with lock:
            cache.clear()
            hits = misses = 0

    def cache_info():
        with lock:
            return info(hits, misses)

    wrapper.cache_clear = cache_clear
    wrapper.cache_info = cache_info
    return wrapper


def unlocked_info(func, cache, key, info):
    hits = misses = 0

    def wrapper(*args, **kwargs):
        nonlocal hits, misses
        k = key(*args, **kwargs)
        try:
            result = cache[k]
            hits += 1
            return result
        except KeyError:
            misses += 1
        v = func(*args, **kwargs)
        try:
            cache[k] = v
        except ValueError:
            pass  # value too large
        return v

    def cache_clear():
        nonlocal hits, misses
        cache.clear()
        hits = misses = 0

    def cache_info():
        return info(hits, misses)

    wrapper.cache_clear = cache_clear
    wrapper.cache_info = cache_info
    return wrapper


def condition(func, cache, key, lock, cond):
    pending = set()

    def wrapper(*args, **kwargs):
        k = key(*args, **kwargs)
        with lock:
            cond.wait_for(lambda: k not in pending)
            try:
                result = cache[k]
                return result
            except KeyError:
                pending.add(k)
        try:
            v = func(*args, **kwargs)
            with lock:
                try:
                    cache[k] = v
                except ValueError:
                    pass  # value too large
                return v
        finally:
            with lock:
                pending.remove(k)
                cond.notify_all()

    def cache_clear():
        with lock:
            cache.clear()

    wrapper.cache_clear = cache_clear
    return wrapper


def locked(func, cache, key, lock):
    def wrapper(*args, **kwargs):
        k = key(*args, **kwargs)
        with lock:
            try:
                return cache[k]
            except KeyError:
                pass  # key not found
        v = func(*args, **kwargs)
        with lock:
            try:
                # In case of a race condition, i.e. if another thread
                # stored a value for this key while we were calling
                # func(), prefer the cached value.
                return cache.setdefault(k, v)
            except ValueError:
                return v  # value too large

    def cache_clear():
        with lock:
            cache.clear()

    wrapper.cache_clear = cache_clear
    return wrapper


def unlocked(func, cache, key):
    def wrapper(*args, **kwargs):
        k = key(*args, **kwargs)
        try:
            return cache[k]
        except KeyError:
            pass  # key not found
        v = func(*args, **kwargs)
        try:
            cache[k] = v
        except ValueError:
            pass  # value too large
        return v

    wrapper.cache_clear = lambda: cache.clear()
    return wrapper


def uncached(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    wrapper.cache_clear = lambda: None
    return wrapper


def wrapper(func, cache, key, lock=None, cond=None, info=None):
    if info is not None:
        if cache is None:
            _wrapper = uncached_info(func, info)
        elif cond is not None and lock is not None:
            _wrapper = condition_info(func, cache, key, lock, cond, info)
        elif cond is not None:
            _wrapper = condition_info(func, cache, key, cond, cond, info)
        elif lock is not None:
            _wrapper = locked_info(func, cache, key, lock, info)
        else:
            _wrapper = unlocked_info(func, cache, key, info)
    else:
        if cache is None:
            _wrapper = uncached(func)
        elif cond is not None and lock is not None:
            _wrapper = condition(func, cache, key, lock, cond)
        elif cond is not None:
            _wrapper = condition(func, cache, key, cond, cond)
        elif lock is not None:
            _wrapper = locked(func, cache, key, lock)
        else:
            _wrapper = unlocked(func, cache, key)
        _wrapper.cache_info = None

    _wrapper.cache = cache
    _wrapper.cache_key = key
    _wrapper.cache_lock = lock if lock is not None else cond
    _wrapper.cache_condition = cond

    return functools.update_wrapper(_wrapper, func)
