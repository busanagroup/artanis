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

from multiprocessing.context import BaseContext
from multiprocessing.synchronize import Event
from pickle import PicklingError

from taskiq.cli.worker.args import WorkerArgs

from artanis.abc.subsys import Subsystem
from artanis.abc.factory import WorkerFactory
from artanis.config import Configuration
from artanis.taskiq.worker import taskiq_worker


class BatchJobWorkerFactory(WorkerFactory):
    worker_name = 'jobs_worker'

    def create_worker(self, processes: list, ctx: BaseContext, shutdown_event: Event, index: int):
        parent: BatchJobSubsystem = self.get_parent()
        worker_args: WorkerArgs = parent.worker_args
        sys_config: Configuration = parent.get_configuration()
        subsys_name: str = parent.subsystem_name
        subsys_index: int = index
        process = ctx.Process(
            # type: ignore
            target=taskiq_worker,
            kwargs={"sysconfig_path": sys_config.config_path, "args": worker_args, "debug": False,
                    "shutdown_event": shutdown_event, "subsys_name": subsys_name, "subsys_index": subsys_index},
        )
        process.daemon = True
        try:
            process.start()
            processes.append((process, self.get_worker_name()))
        except PicklingError as error:
            raise RuntimeError(
                "Cannot pickle the config, see https://docs.python.org/3/library/pickle.html#pickle-picklable"
                # noqa: E501
            ) from error


class BatchJobSubsystem(Subsystem):
    config_service_enabled = Configuration.ARTANIS_TASK_ENABLED
    class_factory = BatchJobWorkerFactory
    worker_args: WorkerArgs
    subsystem_name = 'jobsub'

    def do_configure(self):
        config: Configuration = self.get_configuration()
        self.process_count = 1
        pool_process = config.get_property_value(config.ARTANIS_TASK_INSTANCES, '2')
        params = ['--use-process-pool']
        params.extend(['--max-process-pool-processes', pool_process])
        params.append('--use-process-pool')
        # params.extend(['--log-format', config.log_format[0]])
        params.extend(['--max-async-tasks', config.get_property_value(config.ARTANIS_TASK_MAXTASK, '32')])
        params.append('artanis.taskiq.broker:broker')
        params.append('artanis.taskiq.tasks')
        params.append('artanis.taskiq.scheduler')
        self.worker_args = WorkerArgs.from_cli(params)
