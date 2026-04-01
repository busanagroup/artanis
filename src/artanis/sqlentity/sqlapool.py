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
import enum
import time
from typing import Any
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union

from sqlalchemy import exc
from sqlalchemy import util
from sqlalchemy.pool import QueuePool
from sqlalchemy.pool.base import ConnectionPoolEntry
from sqlalchemy.pool.base import _AsyncConnDialect
from sqlalchemy.pool.base import _CreatorFnType
from sqlalchemy.pool.base import _CreatorWRecFnType
from sqlalchemy.util import queue as sqla_queue
from sqlalchemy.util.langhelpers import memoized_property
from sqlalchemy.util.concurrency import greenlet_spawn

_T = TypeVar("_T", bound=Any)

queue_list = list()
LOOP_TIME_MAX = 2


class AllPendingClose(Exception):
    """Exception raised by Queue.get(block=0)/get_nowait()."""
    pass


@enum.unique
class ConnectionStates(enum.Enum):
    ACTIVE = 1
    IDLE = 2
    PENDING_CLOSE = 3


class QueueProcess(object):
    def __init__(self, queue, pool):
        self.queue = queue
        self.pool = pool

    async def do_monitor_queue(self):
        await greenlet_spawn(self.queue.perform_health_check, self.pool)


class QueueItem(object):
    def __init__(self, item, state: ConnectionStates = ConnectionStates.ACTIVE):
        self.state: ConnectionStates | None = None
        self.item = item
        self.start_time = time.time()
        self.set_state(state)

    def set_state(self, new_state: ConnectionStates):
        if self.state != new_state:
            self.state = new_state
            self.start_time = time.time()

    def get_state(self) -> ConnectionStates:
        return self.state

    def get_start_time(self):
        return self.start_time

    def get_item(self):
        return self.item

    def release_item(self):
        item = self.item
        self.item = None
        return item


class AsyncBaseQueue(asyncio.Queue):

    def popleft(self):
        ...

    def appendleft(self, item):
        ...

    def append(self, item):
        ...


class AsyncFifoQueue(AsyncBaseQueue):

    def _init(self, maxsize):
        self._queue = []

    def _get(self):
        item = self._queue.pop(0)
        if (item.get_state() != ConnectionStates.PENDING_CLOSE) and (item.get_item().connection is None):
            item.set_state(ConnectionStates.PENDING_CLOSE)
        if item.get_state() == ConnectionStates.PENDING_CLOSE:
            old_item = None
            while old_item != item:
                if old_item is None:
                    old_item = item
                self._queue.append(item)
                item = self._queue.pop(0)
                if item.get_state() != ConnectionStates.PENDING_CLOSE:
                    if item.get_item().connection:
                        break
                    else:
                        item.set_state(ConnectionStates.PENDING_CLOSE)
            if item.get_state() == ConnectionStates.PENDING_CLOSE:
                self._queue.append(item)
                raise AllPendingClose
        return item

    def popleft(self):
        return self._queue.pop(0)

    def appendleft(self, item):
        return self._queue.insert(0, item)

    def append(self, item):
        return self._queue.append(item)


class AsyncLifoQueue(AsyncBaseQueue):
    def _init(self, maxsize):
        self._queue = []

    def _put(self, item):
        self._queue.append(item)

    def _get(self):
        item = self._queue.pop()
        if item.get_state() == ConnectionStates.PENDING_CLOSE:
            old_item = None
            while old_item != item:
                if old_item is None:
                    old_item = item
                self._queue.insert(0, item)
                item = self._queue.pop()
                if item.get_state() != ConnectionStates.PENDING_CLOSE:
                    break
            if item.get_state() == ConnectionStates.PENDING_CLOSE:
                self._queue.append(item)
                raise AllPendingClose
        return item

    def popleft(self):
        return self._queue.pop(0)

    def appendleft(self, item):
        return self._queue.insert(0, item)

    def append(self, item):
        return self._queue.append(item)


class BaseActiveQueue(sqla_queue.AsyncAdaptedQueue):

    def perform_health_check(self, pool):
        ...


class AsyncActiveQueue(BaseActiveQueue):
    def __init__(self, maxsize: int = 0, use_lifo: bool = False,
                 max_activetime: int = 300, max_idletime: int = 300):
        super(AsyncActiveQueue, self).__init__(maxsize=maxsize, use_lifo=use_lifo)
        self.max_activetime = max_activetime
        self.max_idletime = max_idletime

    @memoized_property
    def _queue(self) -> AsyncBaseQueue[_T]:

        queue: AsyncBaseQueue[_T]
        if self.use_lifo:
            queue = AsyncLifoQueue(maxsize=self.maxsize)
        else:
            queue = AsyncFifoQueue(maxsize=self.maxsize)
        return queue

    def put(self, item: _T, block: bool = True, timeout: Optional[float] = None) -> None:
        queue_item = QueueItem(item)
        if item.connection is None:
            queue_item.set_state(ConnectionStates.PENDING_CLOSE)
        else:
            start_time = None
            if hasattr(item, 'start_time'):
                start_time = getattr(item, 'start_time', None)
            if start_time:
                elapsed_time = time.time() - start_time
                total_time = self.max_activetime + self.max_idletime
                if elapsed_time > total_time:
                    queue_item.set_state(ConnectionStates.PENDING_CLOSE)
        super(AsyncActiveQueue, self).put(queue_item, block=block, timeout=timeout)

    def get(self, block: bool = True, timeout: Optional[float] = None) -> _T:
        queue_item = super().get(block, timeout=timeout)
        item = queue_item.release_item()
        if queue_item.get_state() == ConnectionStates.PENDING_CLOSE:
            start_time = queue_item.get_start_time()
            setattr(item, 'start_time', start_time)
        return item

    def do_getitem(self):
        return self._queue.popleft()

    def do_putitem(self, item: Any, left=False):
        self._queue.appendleft(item) if self.use_lifo else self._queue.append(item)

    def perform_health_check(self, pool):
        if not self.empty():
            item: QueueItem | None
            item = self.do_getitem()
            old_item = None
            loop_time = time.time()
            while old_item != item:
                now = time.time()
                elapsed_time = now - item.get_start_time()
                if (now - loop_time) > LOOP_TIME_MAX:
                    break
                if old_item is None:
                    old_item = item
                current_state = item.get_state()
                if current_state == ConnectionStates.ACTIVE:
                    if elapsed_time > self.max_activetime:
                        item.set_state(ConnectionStates.IDLE)
                    self.do_putitem(item)
                elif current_state == ConnectionStates.IDLE:
                    if elapsed_time > self.max_idletime:
                        try:
                            conn = item.get_item()
                            conn.close()
                            pool._dec_overflow()
                            if old_item == item:
                                old_item = None
                            item.release_item()
                            item = None
                        except:
                            item.set_state(ConnectionStates.PENDING_CLOSE)
                            self.do_putitem(item)
                    else:
                        self.do_putitem(item)
                elif current_state == ConnectionStates.PENDING_CLOSE:
                    try:
                        conn = item.get_item()
                        conn.close()
                        pool._dec_overflow()
                        if old_item == item:
                            old_item = None
                        item.release_item()
                        item = None
                    except:
                        item.set_state(ConnectionStates.PENDING_CLOSE)
                        self.do_putitem(item)

                if self._queue.empty():
                    break
                item = self.do_getitem()

            if item is not None:
                self.do_putitem(item)


class AsyncQueuePool(QueuePool):
    _is_asyncio = True
    _queue_class: Type[BaseActiveQueue] = (
        AsyncActiveQueue
    )

    _dialect = _AsyncConnDialect()
    _pool: BaseActiveQueue[ConnectionPoolEntry]

    def __init__(
            self,
            creator: Union[_CreatorFnType, _CreatorWRecFnType],
            pool_size: int = 5,
            max_overflow: int = 10,
            timeout: float = 30.0,
            use_lifo: bool = False,
            **kw: Any):
        super(AsyncQueuePool, self).__init__(creator, pool_size=pool_size, max_overflow=max_overflow,
                                             timeout=timeout, use_lifo=use_lifo, **kw)
        self.monitor = QueueProcess(self._pool, self)
        queue_list.append(self.monitor)

    def _do_get(self) -> ConnectionPoolEntry:
        use_overflow = self._max_overflow > -1
        wait = use_overflow and self._overflow >= self._max_overflow
        try:
            return self._pool.get(wait, self._timeout)
        except AllPendingClose:
            self.logger.debug("All connection in queue is PENDING_CLOSE, Forcing pool health check...")
            self._pool.perform_health_check(self)
            return self._do_get()
        except sqla_queue.Empty:
            # don't do things inside of "except Empty", because when we say
            # we timed out or can't connect and raise, Python 3 tells
            # people the real error is queue.Empty which it isn't.
            pass
        if use_overflow and self._overflow >= self._max_overflow:
            if not wait:
                return self._do_get()
            else:
                raise exc.TimeoutError(
                    "QueuePool limit of size %d overflow %d reached, "
                    "connection timed out, timeout %0.2f"
                    % (self.size(), self.overflow(), self._timeout),
                    code="3o7r",
                )

        if self._inc_overflow():
            try:
                return self._create_connection()
            except:
                with util.safe_reraise():
                    self._dec_overflow()
                raise
        else:
            return self._do_get()

    def dispose(self) -> None:
        queue_list.remove(self.monitor)
        self.monitor.queue = None
        self.monitor = None
        while True:
            try:
                conn = self._pool.get(False)
                conn.close()
            except sqla_queue.Empty:
                break
            except Exception:
                ...

        self._overflow = 0 - self.size()


async def do_monitor_queue():
    if len(queue_list) > 0:
        for queue in queue_list:
            await queue.do_monitor_queue()
