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
import threading
from functools import partial
from multiprocessing.context import BaseContext
from multiprocessing.synchronize import Event as EventType
from time import sleep

from artanis.abc.factory import WorkerFactory
from artanis.abc.startable import Startable
from artanis.abc.subsys import Subsystem
from artanis.component.redislite.client import Redis
from artanis.config import Configuration
from artanis.utils import threaded_check_multiprocess_shutdown_event


class SupervisorFactory(WorkerFactory):
    worker_name = 'spv_worker'
    passed: int = 0
    last_exception: Exception

    def create_worker(self, processes: list, ctx: BaseContext, shutdown_event: EventType, index: int):

        def threaded_supervisor():
            parent = self.get_parent()
            self.passed = 0
            try:
                params = parent.params
                kwargs = params[1]
                dbfilename = kwargs.pop("dbfilename")
                redis_cmp: Redis = Redis(
                    dbfilename,
                    host=kwargs["bind"],
                    port=kwargs["port"],
                    password=kwargs["requirepass"],
                    serverconfig=kwargs,
                )
                self.passed = 1
                shutdown_trigger = None
                if shutdown_event is not None:
                    shutdown_trigger = partial(threaded_check_multiprocess_shutdown_event, shutdown_event, sleep)

                try:
                    shutdown_trigger()
                finally:
                    sleep(0.5)
                    redis_cmp.shutdown(save=True, force=True)
                    parent: Startable = self.get_parent()
                    parent.stop()
            except Exception as e:
                self.passed = 9
                self.last_exception = e

        thread = threading.Thread(target=threaded_supervisor)
        thread.start()

    def should_be_waited(self):
        return True

    def process_passed(self) -> int:
        return self.passed

    def get_last_exception(self) -> Exception | None:
        return self.last_exception


class SupervisorSubsystem(Subsystem):
    config_service_enabled = Configuration.ARTANIS_SPV_ENABLED
    class_factory = SupervisorFactory
    subsystem_name = 'spvsub'
    params: list

    def do_configure(self):
        config: Configuration = self.get_configuration()
        host, port = f"{config.get_property_value(Configuration.ARTANIS_SPV_BIND, "127.0.0.1:8090")}".split(":")
        redis_db = f"{config.get_property_value(Configuration.ARTANIS_DATA_PATH)}/supervisor.db"
        log_file = f"{config.get_property_value(Configuration.ARTANIS_LOG_PATH)}/redis.log"
        passwd = config.get_property_value(Configuration.ARTANIS_SPV_SECURITY_HASH)
        self.process_count = 1
        self.params = [
            [],
            dict(bind=host, port=port, dbfilename=redis_db, requirepass=passwd, logfile=log_file, loglevel='warning')
        ]
