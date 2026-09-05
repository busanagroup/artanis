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
from taskiq.cli.worker.args import WorkerArgs

from artanis.abc.subsys import Subsystem
from artanis.config import Configuration
from artanis.subsys.batchjob import BatchJobWorkerFactory


class EventBusWorkerFactory(BatchJobWorkerFactory):
    worker_name = 'eventbus_worker'


class EventBusSubsystem(Subsystem):
    config_service_enabled = Configuration.ARTANIS_SPV_ENABLED
    class_factory = EventBusWorkerFactory
    worker_args: WorkerArgs
    subsystem_name = 'eventbus'

    def do_configure(self):
        config: Configuration = self.get_configuration()
        self.process_count = int(config.get_property_value(config.ARTANIS_EVENT_INSTANCES, '2'))
        params = ['--use-process-pool']
        params.extend(['--max-process-pool-processes', config.get_property_value(config.ARTANIS_EVENT_PROCESSES, '2')])
        params.append('--use-process-pool')
        # params.extend(['--log-format', config.log_format[0]])
        params.extend(['--max-async-tasks', config.get_property_value(config.ARTANIS_EVENT_MAXEVENT, '32')])
        params.extend(['--max-prefetch', '4'])
        params.append('artanis.taskiq.broker:event_broker')
        params.append('artanis.taskiq.tasks')
        params.append('artanis.taskiq.scheduler')
        self.worker_args = WorkerArgs.from_cli(params)
