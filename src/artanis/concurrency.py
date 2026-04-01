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
import asyncio
import functools
import inspect
import multiprocessing
import typing as t

__all__ = ["is_async", "run", "run_task_group", "AsyncProcess"]

R = t.TypeVar("R", covariant=True)
P = t.ParamSpec("P")


def is_async(obj: t.Any) -> t.TypeGuard[t.Callable[..., t.Awaitable[t.Any]]]:
    """Check if given object is an async function, callable or partialised function.

    :param obj: Object to check.
    :return: True if it's an async function, callable or partialised function.
    """
    while isinstance(obj, functools.partial):
        obj = obj.func

    return inspect.iscoroutinefunction(obj) or inspect.iscoroutinefunction(getattr(obj, "__call__"))


async def run(
        func: t.Callable[P, R] | t.Callable[P, t.Awaitable[R]],
        *args: P.args,
        **kwargs: P.kwargs,
) -> R:
    """Run a function either as asyncio awaiting it if it's an async function or running it in a thread if it's a
    sync function.

    :param func: Function to run.
    :param args: Positional arguments.
    :param kwargs: Keyword arguments.
    :return: Function returned value.
    """
    if is_async(func):
        return await func(*args, **kwargs)

    return t.cast(R, await asyncio.to_thread(func, *args, **kwargs))


async def run_task_group(*tasks: t.Coroutine[t.Any, t.Any, t.Any]) -> list[asyncio.Task]:
    """Run a group of tasks.

    :param tasks: Tasks to run.
    :result: Finished tasks.
    """
    async with asyncio.TaskGroup() as task_group:
        return [task_group.create_task(task) for task in tasks]


class AsyncProcess(multiprocessing.Process):
    """Multiprocessing Process class whose target is an async function."""

    _target: t.Callable[..., t.Any | t.Coroutine] | None
    _args: list[t.Any]
    _kwargs: dict[str, t.Any]

    def run(self) -> None:
        if self._target:
            result_or_task = self._target(*self._args, **self._kwargs)

            asyncio.run(result_or_task) if is_async(self._target) else result_or_task
