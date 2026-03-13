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
import inspect
import signal
from typing import Any
from multiprocessing.synchronize import Event as EventType
from concurrent.futures import Executor, ProcessPoolExecutor, ThreadPoolExecutor

import uvloop
from taskiq import AsyncBroker
from taskiq.cli.utils import import_object, import_tasks
from taskiq.cli.worker.args import WorkerArgs
from taskiq.cli.worker.run import get_receiver_type

from artanis.config import Configuration
from artanis.logging import install_mp_handler


async def shutdown_broker(broker: AsyncBroker, timeout: float) -> None:
    try:
        await asyncio.wait_for(broker.shutdown(), timeout)  # type: ignore
    except asyncio.TimeoutError:
        ...
    except Exception as exc:
        ...


def taskiq_worker(sysconfig_path: Configuration, args: WorkerArgs, debug: bool, shutdown_event: EventType) -> None:
    hardkill_counter = 0
    config = Configuration.get_default_instance(config_path=sysconfig_path)
    config.configure_logging()
    install_mp_handler()


    def interrupt_handler(signum: int, _frame: Any) -> None:
        """
        Signal handler.

        This handler checks if process is already
        terminating and if it's true, it does nothing.

        :param signum: received signal number.
        :param _frame: current execution frame.
        :raises KeyboardInterrupt: if termination hasn't begun.
        """
        nonlocal shutdown_event
        nonlocal hardkill_counter
        # Soft kill is a signal to start shutdown.
        shutdown_event.set()
        # Hard kill is a signal that we should stop
        # everything immediately.
        if hardkill_counter > args.hardkill_count:
            raise KeyboardInterrupt
        hardkill_counter += 1

    signal.signal(signal.SIGINT, interrupt_handler)
    signal.signal(signal.SIGTERM, interrupt_handler)
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)

    # This option signals that current
    # broker is running as a worker.
    # We must set this field before importing tasks,
    # so broker will remember all tasks it's related to.

    broker = import_object(args.broker)
    if inspect.isfunction(broker):
        broker = broker()
    if not isinstance(broker, AsyncBroker):
        raise ValueError(
            "Unknown broker type. Please use AsyncBroker instance "
            "or pass broker factory function that returns an AsyncBroker instance.",
        )

    broker.is_worker_process = True
    import_tasks(args.modules, args.tasks_pattern, args.fs_discover)

    receiver_type = get_receiver_type(args)
    receiver_kwargs = dict(args.receiver_arg)
    executor: Executor = ProcessPoolExecutor(max_workers=args.max_process_pool_processes)
    try:
        with executor as pool:
            receiver = receiver_type(
                broker=broker,
                executor=pool,
                validate_params=not args.no_parse,
                max_async_tasks=args.max_async_tasks,
                max_prefetch=args.max_prefetch,
                propagate_exceptions=not args.no_propagate_errors,
                ack_type=args.ack_type,
                max_tasks_to_execute=args.max_tasks_per_child,
                wait_tasks_timeout=args.wait_tasks_timeout,
                **receiver_kwargs,  # type: ignore
            )
            loop.run_until_complete(receiver.listen(shutdown_event))
    finally:
        loop.run_until_complete(shutdown_broker(broker, args.shutdown_timeout))
