#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2025 Busana Apparel Group. All rights reserved.
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

import inspect
from typing import Callable

from artanis import patch
from artanis.config import Configuration
from artanis.utils import import_function

do_monitor_queue: Callable | None = None


async def artanis_startup(config: Configuration):
    config.server_is_ready = False
    try:
        broker = import_function("artanis.taskiq.broker:broker")
        config.container.redis_pool = broker.get_redis_pool()
        patch.perform_patch()
        function = import_function("ecf.core.entrypoint:do_startup")
        if inspect.iscoroutinefunction(function):
            await function()
    finally:
        config.server_is_ready = True


async def artanis_shutdown(config: Configuration):
    try:
        function = import_function("ecf.core.entrypoint:do_shutdown")
        if inspect.iscoroutinefunction(function):
            await function()
    finally:
        config.server_is_ready = False


async def artanis_monitor(config: Configuration):
    global do_monitor_queue
    if not do_monitor_queue:
        do_monitor_queue = import_function("artanis.sqlentity.sqlapool:do_monitor_queue")
    try:
        await do_monitor_queue()
    except:
        pass
