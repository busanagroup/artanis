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
import threading
from functools import partial
from multiprocessing.context import BaseContext
from multiprocessing.synchronize import Event

import uvloop
from taskiq.cli.scheduler.args import SchedulerArgs

from artanis.abc.factory import WorkerFactory
from artanis.abc.subsys import Subsystem
from artanis.config import Configuration
from artanis.taskiq.worker import run_scheduler
from artanis.utils import check_multiprocess_shutdown_event


class SchedulerWorkerFactory(WorkerFactory):
    worker_name = 'sch_worker'

    def create_worker(self, processes: list, ctx: BaseContext, shutdown_event: Event, index: int):
        parent = self.get_parent()
        parsed = SchedulerArgs.from_cli(parent.params)

        def threaded_scheduler():
            loop = uvloop.new_event_loop
            shutdown_trigger = None
            if shutdown_event is not None:
                shutdown_trigger = partial(check_multiprocess_shutdown_event, shutdown_event, asyncio.sleep)

            with asyncio.Runner(debug=False, loop_factory=loop) as runner:
                runner.run(run_scheduler(parsed, shutdown_trigger=shutdown_trigger))

        thread = threading.Thread(target=threaded_scheduler)
        thread.start()


class SchedulerSubsystem(Subsystem):
    config_service_enabled = Configuration.ARTANIS_SPV_ENABLED
    class_factory = SchedulerWorkerFactory
    subsystem_name = 'schsub'
    params: list

    def do_configure(self):
        self.process_count = 1
        self.params = []
        self.params.append('artanis.taskiq.scheduler:scheduler')
        self.params.append('--skip-first-run')
