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
# This module is part of Centric PLM Integration Bridge and is released under
# the Apache-2.0 License: https://www.apache.org/licenses/LICENSE-2.0
from __future__ import annotations

from multiprocessing.context import BaseContext
from multiprocessing.synchronize import Event
from pickle import PicklingError

from hypercorn.config import Config, Sockets
from hypercorn.asyncio.run import uvloop_worker

from artanis.abc.subsys import Subsystem
from artanis.abc.factory import WorkerFactory
from artanis.config import Configuration
from artanis.logging import install_mp_handler


def hypercorn_worker(
        sysconfig_path: Configuration, asgi_config: Config, sockets: Sockets | None = None,
        shutdown_event: Event | None = None
) -> None:
    config = Configuration.get_default_instance(config_path=sysconfig_path)
    config.configure_logging()
    install_mp_handler()
    uvloop_worker(asgi_config, sockets=sockets, shutdown_event=shutdown_event)


class ASGIWorkerFactory(WorkerFactory):
    worker_name = 'asgi_worker'

    def create_worker(self, processes: list, ctx: BaseContext, shutdown_event: Event):
        parent = self.get_parent()
        sys_config = parent.get_configuration()
        config = parent.asgi_config
        sockets = parent.sockets
        process = ctx.Process(  # type: ignore
            target=hypercorn_worker,
            kwargs={"sysconfig_path": sys_config.config_path, "asgi_config": config, "shutdown_event": shutdown_event,
                    "sockets": sockets},
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


class ASGISubsystem(Subsystem):
    config_bind_type: str
    config_bind: str
    config_process_instances: str


    def __init__(self, config=None):
        super().__init__(config=config)
        self.asgi_config = Config()
        self.sockets = None
        self.process_count = int(config.get_property_value(self.config_process_instances))

    def do_configure(self):
        config: Configuration = self.get_configuration()
        self.asgi_config.worker_class = 'uvloop'
        self.asgi_config.workers = self.process_count
        if self.use_unix_socket:
            self.asgi_config.bind = self.unix_socket_path
        else:
            self.asgi_config.bind = [config.get_property_value(self.config_bind)]

    def do_start(self):
        self.sockets = self.asgi_config.create_sockets()

    @property
    def use_unix_socket(self):
        config: Configuration = self.get_configuration()
        return config.get_property_value(self.config_bind_type, "unix").lower() == "unix"

    @property
    def unix_socket_path(self):
        config: Configuration = self.get_configuration()
        return "{}/{}.sock".format(config.get_property_value(config.ARTANIS_TMP_PATH, None), self.subsystem_name)
