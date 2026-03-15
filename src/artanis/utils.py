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

import os
import sys
from pathlib import Path
from importlib import import_module
from collections.abc import Callable, Awaitable
from multiprocessing.synchronize import Event as EventType
from typing import Any

from artanis.exceptions import ShutdownError, NoAppError


def write_pid_file(pid_path: str) -> None:
    with open(pid_path, "w") as file_:
        file_.write(f"{os.getpid()}")


async def raise_shutdown(shutdown_event: Callable[..., Awaitable]) -> None:
    await shutdown_event()
    raise ShutdownError()


async def check_multiprocess_shutdown_event(
        shutdown_event: EventType, sleep: Callable[[float], Awaitable[Any]]
) -> None:
    while True:
        if shutdown_event.is_set():
            return
        await sleep(0.1)


def import_function(path: str, attach=None):
    module_name, func_name = path.split(":", 1)
    module_path = Path(module_name).resolve()
    path_str = str(module_path.parent)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
    if module_path.is_file():
        import_name = module_path.with_suffix("").name
    else:
        import_name = module_path.name
    try:
        module = import_module(import_name)
    except ModuleNotFoundError as error:
        if error.name == import_name:
            raise NoAppError(f"Cannot load function from '{module_path}', module not found.")
        else:
            raise
    try:
        func = eval(func_name, vars(module))
    except NameError:
        raise NoAppError(f"Cannot load application from '{module_path}', application not found.")

    if attach:
        setattr(attach, func_name, func)
    return func
