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
import logging
import signal
import sys
from asyncio import TaskGroup
from concurrent.futures import Executor, ProcessPoolExecutor
from datetime import timedelta
from multiprocessing.synchronize import Event as EventType
from typing import Any, Awaitable, Callable

import uvloop
from taskiq import AsyncBroker, TaskiqScheduler
from taskiq.cli.scheduler.args import SchedulerArgs
from taskiq.cli.scheduler.run import SchedulerLoop
from taskiq.cli.utils import import_object, import_tasks
from taskiq.cli.worker.args import WorkerArgs
from taskiq.cli.worker.run import get_receiver_type

from artanis.config import Configuration
from artanis.exceptions import ShutdownError
from artanis.utils import raise_shutdown

worker_logger = logging.getLogger("taskiq.worker")

async def shutdown_broker(broker: AsyncBroker, timeout: float) -> None:
    worker_logger.warning("Shutting down the broker.")
    try:
        ret_val = await asyncio.wait_for(broker.shutdown(), timeout)  # type: ignore
        if ret_val is not None:
            worker_logger.info("Broker has returned value on shutdown: '%s'", str(ret_val))
    except asyncio.TimeoutError:
        worker_logger.warning("Broker.shutdown cannot be completed in %s seconds.", timeout)
    except Exception as exc:
        worker_logger.warning(
            "Exception found while shutting down broker: %s",
            exc,
            exc_info=True,
        )


def taskiq_worker(
        sysconfig_path: Configuration,
        args: WorkerArgs,
        debug: bool,
        shutdown_event: EventType,
        subsys_name: str,
        subsys_index: int
) -> None:
    hardkill_counter = 0
    config = Configuration.get_default_instance(config_path=sysconfig_path)
    config.configure_logging(config.configure_logging(subsys_name=subsys_name, subsys_index=subsys_index))

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
            worker_logger.warning("Hard kill. Exiting.")
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

scheduler_logger = logging.getLogger("taskiq.scheduler")

async def scheduler_worker(args: SchedulerArgs):
    if isinstance(args.scheduler, str):
        scheduler = import_object(args.scheduler, app_dir=args.app_dir)
        if inspect.isfunction(scheduler):
            scheduler = scheduler()
    else:
        scheduler = args.scheduler
    if not isinstance(scheduler, TaskiqScheduler):
        scheduler_logger.error(
                    "Imported scheduler is not a subclass of TaskiqScheduler.",
                )
        sys.exit(1)

    scheduler.broker.is_scheduler_process = True
    import_tasks(args.modules, args.tasks_pattern, args.fs_discover)
    for source in scheduler.sources:
        await source.startup()

    update_interval = timedelta(seconds=60)
    if args.update_interval is not None:
        update_interval = timedelta(seconds=args.update_interval)

    loop_interval = timedelta(seconds=1)
    if args.loop_interval is not None:
        loop_interval = timedelta(seconds=args.loop_interval)

    scheduler_logger.info("Starting scheduler.")
    await scheduler.startup()
    scheduler_logger.info("Startup completed.")

    scheduler_loop = SchedulerLoop(scheduler)
    try:
        await scheduler_loop.run(
            update_interval=update_interval,
            loop_interval=loop_interval,
            skip_first_run=args.skip_first_run,
        )
    except asyncio.CancelledError:
        scheduler_logger.warning("Shutting down scheduler.")
        await scheduler.shutdown()
        for source in scheduler.sources:
            await source.shutdown()
        scheduler_logger.info("Scheduler shut down. Good bye!")


async def run_scheduler(args: SchedulerArgs,
                        shutdown_trigger: Callable[..., Awaitable] | None = None):
    loop = asyncio.get_event_loop()
    if shutdown_trigger is None:
        signal_event = asyncio.Event()

        def _signal_handler(*_: Any) -> None:  # noqa: N803
            signal_event.set()

        for signal_name in {"SIGINT", "SIGTERM", "SIGBREAK"}:
            if hasattr(signal, signal_name):
                try:
                    loop.add_signal_handler(getattr(signal, signal_name), _signal_handler)
                except NotImplementedError:
                    # Add signal handler may not be implemented on Windows
                    signal.signal(getattr(signal, signal_name), _signal_handler)

        shutdown_trigger = signal_event.wait

    try:
        async with TaskGroup() as task_group:
            task_group.create_task(raise_shutdown(shutdown_trigger))
            task_group.create_task(scheduler_worker(args))
    except BaseExceptionGroup as error:
        _, other_errors = error.split((ShutdownError, KeyboardInterrupt))
        if other_errors is not None:
            raise other_errors
    except (ShutdownError, KeyboardInterrupt):
        pass

