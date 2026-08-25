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


import inspect

from artanis import patch
from artanis.config import Configuration
from artanis.utils import import_function

entry_points = [
    'artanis.taskiq.entrypoint',
    'artanis.component.entrypoint',
    'artanis.sqlentity.entrypoint',
    'ecf.core.entrypoint',
]


def import_entrypoint_function(module_path: str, function_name: str):
    try:
        function = import_function(f"{module_path}:{function_name}")
        return function
    except Exception as e:
        print(f"Error importing {function_name} from {module_path}: {e}")
        return None


async def artanis_startup(config: Configuration):
    global entry_points
    config.server_is_ready = False
    try:
        patch.perform_patch()
        for entry_point in entry_points:
            startup_function = import_entrypoint_function(entry_point, "artanis_startup")
            if startup_function:
                if inspect.iscoroutinefunction(startup_function):
                    await startup_function(config)
                else:
                    startup_function(config)
    finally:
        config.server_is_ready = True


async def artanis_shutdown(config: Configuration):
    global entry_points
    try:
        for entry_point in reversed(entry_points):
            shutdown_function = import_entrypoint_function(entry_point, "artanis_shutdown")
            if shutdown_function:
                if inspect.iscoroutinefunction(shutdown_function):
                    await shutdown_function(config)
                else:
                    shutdown_function(config)
    finally:
        config.server_is_ready = False


async def artanis_monitor(config: Configuration):
    pass
