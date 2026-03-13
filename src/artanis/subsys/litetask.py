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

from taskiq.cli.worker.args import WorkerArgs

from artanis.config import Configuration
from artanis.subsys.batchjob import BatchJobSubsystem, BatchJobWorkerFactory

class LiteTaskWorkerFactory(BatchJobWorkerFactory):
    worker_name = 'tasks_worker'

class LiteTaskSubsystem(BatchJobSubsystem):
    class_factory = BatchJobWorkerFactory
    subsystem_name = 'tasksub'

    def do_configure(self):
        config: Configuration = self.get_configuration()
        self.process_count = 1
        params = ['--use-process-pool']
        params.extend(['--max-process-pool-processes', str(self.process_count)])
        params.append('--use-process-pool')
        # params.extend(['--log-format', config.log_format[0]])
        params.extend(['--max-async-tasks', config.get_property_value(config.ARTANIS_TASK_MAXTASK, '32')])
        params.append('artanis.taskiq.broker:task_broker')
        params.append('artanis.taskiq.scheduler')
        self.worker_args = WorkerArgs.from_cli(params)

    @classmethod
    def subsystem_is_enabled(cls, config) -> bool:
        return True