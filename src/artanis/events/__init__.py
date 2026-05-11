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

"""Event bus library."""

from . import sucker as events_suck
from .base import (
    BaseEvent,
    EventConcurrencyMode,
    EventHandlerCompletionMode,
    EventHandlerConcurrencyMode,
    EventResult,
    EventStatus,
    PythonIdentifierStr,
    PythonIdStr,
    UUIDStr,
)
from .eventbus import EventBus
from .handler import (
    EventHandler,
    EventHandlerAbortedError,
    EventHandlerCancelledError,
    EventHandlerResultSchemaError,
    EventHandlerTimeoutError,
)
from .history import EventHistory
from .helpers import monotonic_datetime
from .middlewares import (
    AutoErrorEventMiddleware,
    AutoHandlerChangeEventMiddleware,
    AutoReturnEventMiddleware,
    BusHandlerRegisteredEvent,
    BusHandlerUnregisteredEvent,
    EventBusMiddleware,
    LoggerEventBusMiddleware,
    SQLiteHistoryMirrorMiddleware,
    WALEventBusMiddleware,
)
from .topic import Topic

__all__ = [
    'EventBus',
    'EventBusMiddleware',
    'BusHandlerRegisteredEvent',
    'BusHandlerUnregisteredEvent',
    'LoggerEventBusMiddleware',
    'SQLiteHistoryMirrorMiddleware',
    'AutoErrorEventMiddleware',
    'AutoHandlerChangeEventMiddleware',
    'AutoReturnEventMiddleware',
    'WALEventBusMiddleware',
    'EventHistory',
    'monotonic_datetime',
    'BaseEvent',
    'EventStatus',
    'EventResult',
    'EventHandler',
    'EventHandlerCancelledError',
    'EventHandlerResultSchemaError',
    'EventHandlerTimeoutError',
    'EventHandlerAbortedError',
    'EventHandlerConcurrencyMode',
    'EventHandlerCompletionMode',
    'EventConcurrencyMode',
    'UUIDStr',
    'PythonIdStr',
    'PythonIdentifierStr',
    'events_suck',
    'Topic',
]
