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
from functools import partial

from artanis.broadcast.layers.amqp import carehare
from artanis.broadcast.layers.amqp.multiqueue import MultiQueue
from artanis.broadcast.layers.amqp.utils import deserialize_message


async def consume_into_multi_queue_until_connection_close(
    connection: carehare.Connection,
    exchange_name: str,
    multi_queue: MultiQueue,
    prefetch_count: int,
) -> None:
    loop = asyncio.get_running_loop()

    try:
        async with connection.acking_consumer(
            exchange_name, prefetch_count=prefetch_count
        ) as consumer:

            def _ack_or_no_op(delivery_tag: int):
                try:
                    consumer.ack(delivery_tag)
                except OSError:  # asyncio.Transport.write() failed
                    pass

            while True:
                # back-pressure until `consumer.ack()` was called enough times
                try:
                    body, delivery_tag = await consumer.next_delivery()
                except carehare.ChannelClosed:
                    break
                recipient, data = deserialize_message(body)

                multi_queue.put_nowait(
                    recipient,
                    data,
                    time=loop.time(),
                    ack=partial(_ack_or_no_op, delivery_tag),
                )
    except carehare.ChannelClosed:
        pass
