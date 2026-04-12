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

import functools
import os
import sys
from collections.abc import Callable, Awaitable
from importlib import import_module
from inspect import iscoroutinefunction
from multiprocessing.synchronize import Event as EventType
from pathlib import Path
from typing import Any, overload, TypeVar

import anyio.to_thread
from starlette.types import Scope

from artanis.exceptions import ShutdownError, NoAppError

T = TypeVar("T")
AwaitableCallable = Callable[..., Awaitable[T]]


@overload
def is_async_callable(obj: AwaitableCallable[T]) -> TypeIs[AwaitableCallable[T]]: ...


@overload
def is_async_callable(obj: Any) -> TypeIs[AwaitableCallable[Any]]: ...


def is_async_callable(obj: Any) -> Any:
    while isinstance(obj, functools.partial):
        obj = obj.func

    return iscoroutinefunction(obj) or (callable(obj) and iscoroutinefunction(obj.__call__))


async def run_in_threadpool(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    func = functools.partial(func, *args, **kwargs)
    return await anyio.to_thread.run_sync(func)


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


def import_ecf_module(module_name: str):
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
            raise NoAppError(f"Cannot load application from '{module_path}', module not found.")
        else:
            raise
    except Exception as error:
        raise
    return module


def load_ecf_modules(module_name: str, should_attach: bool = False):
    module = import_ecf_module(module_name)
    attach = module if should_attach else None
    for package in module.__all__:
        import_function(f"{module_name}.{package}:{package}", attach)


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

def get_route_path(scope: Scope) -> str:
    path: str = scope["path"]
    root_path = scope.get("root_path", "")
    if not root_path:
        return path

    if not path.startswith(root_path):
        return path

    if path == root_path:
        return ""

    if path[len(root_path)] == "/":
        return path[len(root_path):]

    return path

def generate_unique_id(route: "Route") -> str:
    operation_id = f"{route.name}{route.path_format}"
    operation_id = re.sub(r"\W", "_", operation_id)
    assert route.methods
    operation_id = f"{operation_id}_{list(route.methods)[0].lower()}"
    return operation_id

def get_name(endpoint: Callable[..., Any]) -> str:
    return getattr(endpoint, "__name__", endpoint.__class__.__name__)