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

import signal
from multiprocessing import get_context
from multiprocessing.connection import wait
from multiprocessing.synchronize import Event as EventType
from typing import Any

from artanis.abc.startable import LifeCycleManager
from artanis.abc.subsys import Subsystem
from artanis.subsys import __all__ as subsys_classes
from artanis.utils import write_pid_file


class Artanis(LifeCycleManager):

    pid_path: str

    def __init__(self, config=None):
        super().__init__(config=config)
        self.factories = []
        self.app_context = None
        self.pid_path = '{}/{}'.format(config.get_property_value(config.ARTANIS_TMP_PATH, None), 'artanis.pid')

    def do_configure(self):
        config = self.get_configuration()
        write_pid_file(self.pid_path)
        self.app_context = get_context("spawn")
        for klass in subsys_classes:
            if issubclass(klass, Subsystem) and klass.subsystem_enabled(config):
                subsys = klass(config=config)
                self.add_object(subsys)

    def do_start(self):
        super().do_start()
        subsys_objects: list = self.get_objects()
        for subsys in subsys_objects:
            subsys.register_factory(self)


    def daemonize(self):
        active = True
        shutdown_event = self.app_context.Event()

        def shutdown(*args: Any) -> None:
            nonlocal active, shutdown_event
            shutdown_event.set()
            active = False

        processes = []
        exitcode = 0
        try:
            while active:
                signal.signal(signal.SIGINT, signal.SIG_IGN)
                self._populate_process(processes, shutdown_event)

                for signal_name in {"SIGINT", "SIGTERM", "SIGBREAK"}:
                    if hasattr(signal, signal_name):
                        signal.signal(getattr(signal, signal_name), shutdown)

                if not processes:
                    break
                wait(process.sentinel for process, worker_name in processes)
                exitcode = self._join_exited(processes)
                if exitcode != 0:
                    shutdown_event.set()
                    active = False
        finally:
            for process, worker_name in processes:
                process.terminate()

        exitcode = self._join_exited(processes) if exitcode != 0 else exitcode
        self.stop()
        return exitcode

    def _populate_process(self, processes: list, shutdown_event: EventType):
        for factory in self.factories:
            process_count = factory.get_processes(processes)
            for index in range(factory.get_process_count() - process_count):
                factory.create_worker(processes, self.app_context, shutdown_event, index)

    def _join_exited(self, processes: list) -> int:
        exitcode = 0
        for index in reversed(range(len(processes))):
            worker, _ = processes[index]
            if worker.exitcode is not None:
                worker.join()
                exitcode = worker.exitcode if exitcode == 0 else exitcode
                del processes[index]

        return exitcode
