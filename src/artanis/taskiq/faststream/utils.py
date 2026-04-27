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
import typing

from fast_depends.utils import is_async_gen_callable, is_gen_callable
from faststream.types import SendableMessage

try:
    from faststream.utils.functions import to_async
except ImportError:
    from faststream._internal.utils import to_async  # type: ignore[no-redef]


async def resolve_msg(
        msg: None
             | SendableMessage
             | typing.Callable[[], SendableMessage]
             | typing.Callable[[], typing.Awaitable[SendableMessage]]
             | typing.Callable[[], typing.Iterator[SendableMessage]]
             | typing.Callable[[], typing.AsyncIterator[SendableMessage]],
) -> typing.AsyncIterator[SendableMessage]:
    """Resolve message generation callback.

    Args:
        msg: object to send or sync/async message generation callback.

    Returns:
        The message to send
    """
    if callable(msg):
        if is_async_gen_callable(msg):
            async for i in typing.cast(
                    typing.Callable[[], typing.AsyncIterator[SendableMessage]],
                    msg,
            )():
                yield i

        elif is_gen_callable(msg):
            for i in typing.cast(
                    typing.Callable[[], typing.Iterator[SendableMessage]],
                    msg,
            )():
                yield i

        else:
            get_msg = typing.cast(
                typing.Callable[[], typing.Awaitable[SendableMessage]],
                to_async(msg),
            )
            yield await get_msg()

    else:
        yield msg
