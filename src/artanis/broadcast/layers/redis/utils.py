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

from asyncio import AbstractEventLoop

import binascii
from typing import Any

from redis import asyncio as aioredis

from artanis.broadcast.layers.redis.defs import ChannelDecodedRedisHost, ChannelRawRedisHost


def consistent_hash(value: str | bytes, ring_size: int) -> int:
    """
    Maps the value to a node value between 0 and 4095
    using CRC, then down to one of the ring nodes.
    """
    if ring_size == 1:
        # Avoid the overhead of hashing and modulo when it is unnecessary.
        return 0

    if isinstance(value, str):
        value = value.encode("utf8")
    bigval = binascii.crc32(value) & 0xFFF
    ring_divisor = 4096 / float(ring_size)
    return int(bigval / ring_divisor)


def wrap_close(
        proxy: "RedisChannelLayer | RedisPubSubChannelLayer", loop: AbstractEventLoop
) -> None:
    """Wrap event loop close to cleanup Redis layers.

    Args:
        proxy: The Redis channel layer proxy to cleanup.
        loop: The event loop to wrap.
    """
    original_impl = loop.close

    def _wrapper(self: AbstractEventLoop, *args: Any, **kwargs: Any) -> None:
        """Wrapper function that cleans up layers before closing the loop."""
        if loop in proxy._layers:  # noqa
            layer = proxy._layers[loop]  # noqa
            del proxy._layers[loop]  # noqa
            loop.run_until_complete(layer.flush())

        self.close = original_impl  # type: ignore[method-assign]
        return self.close(*args, **kwargs)

    loop.close = types.MethodType(_wrapper, loop)  # type: ignore[method-assign]


async def close_redis(connection: aioredis.Redis) -> None:
    """
    Handle compatibility with redis-py 4.x and 5.x close methods
    """
    try:
        await connection.aclose(close_connection_pool=True)
    except AttributeError:
        await connection.close(close_connection_pool=True)


def decode_hosts(
        hosts: list[ChannelRawRedisHost] | None,
) -> list[ChannelDecodedRedisHost]:
    """
    Takes the value of the "hosts" argument and returns
    a list of kwargs to use for the Redis connection constructor.
    """
    # If no hosts were provided, return a default value
    if not hosts:
        return [{"address": "redis://localhost:6379"}]
    # If they provided just a string, scold them.
    if isinstance(hosts, str | bytes):
        raise ValueError(
            "You must pass a list of Redis hosts, even if there is only one."
        )

    # Decode each hosts entry into a kwargs dict
    result: list[ChannelDecodedRedisHost] = []
    for entry in hosts:
        if isinstance(entry, dict):
            result.append(entry)
        elif isinstance(entry, tuple | list):
            result.append({"host": entry[0], "port": entry[1]})
        else:
            result.append({"address": entry})
    return result


def create_pool(host: ChannelDecodedRedisHost) -> aioredis.ConnectionPool:
    """
    Takes the value of the "host" argument and returns a suited connection pool to
    the corresponding redis instance.
    """
    # avoid side-effects from modifying host
    host = host.copy()
    if "address" in host:
        address = host.pop("address")
        return aioredis.ConnectionPool.from_url(address, **host)

    master_name = host.pop("master_name", None)
    if master_name is not None:
        sentinels = host.pop("sentinels")
        sentinel_kwargs = host.pop("sentinel_kwargs", None)
        return aioredis.SentinelConnectionPool(  # type: ignore[no-untyped-call]
            master_name,
            aioredis.Sentinel(sentinels, sentinel_kwargs=sentinel_kwargs),  # type: ignore[no-untyped-call]
            **host,
        )

    return aioredis.ConnectionPool(**host)
