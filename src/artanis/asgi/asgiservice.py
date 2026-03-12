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
# This module is part of Centric PLM Integration Bridge and is released under
# the Apache-2.0 License: https://www.apache.org/licenses/LICENSE-2.0
from __future__ import annotations

import asyncio

from fastapi import FastAPI
from starlette.middleware.gzip import GZipMiddleware

from artanis.abc.service import StartableService
from artanis.abc.singleton import Singleton
from artanis.abc.objlock import SyncLock
from artanis.abc.objloader import ObjectLoader
from artanis.config import Configuration
from artanis.startup import artanis_monitor, artanis_startup, artanis_shutdown


class ASGIService(FastAPI, StartableService, Singleton, SyncLock, ObjectLoader):

    def __init__(self, *args, **kwargs):
        config = kwargs.pop('config')
        super(ASGIService, self).__init__(*args, **kwargs)
        for base in ASGIService.__bases__:
            if base is not FastAPI:
                base.__init__(self, *args, config=config, **kwargs)

    def do_configure(self):
        super(ASGIService, self).do_configure()
        config = self.get_configuration()
        self.configure_modules(config)
        self.configure_services(config)
        self.configure_middlewares(config)
        self.configure_application(config)

        async def internal_scheduler():
            try:
                while True:
                    await asyncio.sleep(60)
                    await artanis_monitor(config)
            except asyncio.CancelledError:
                pass

        async def process_startup():
            loop = asyncio.get_event_loop()
            loop.create_task(internal_scheduler())
            await self.start()
            await artanis_startup(config)

        async def process_shutdown():
            await artanis_shutdown(config)
            await self.stop()

        self.add_event_handler("startup", process_startup)
        self.add_event_handler("shutdown", process_shutdown)

        if self.middleware_stack is None:
            self.middleware_stack = self.build_middleware_stack()

    def configure_modules(self, config):
        ...

    def configure_services(self, config):
        ...

    def configure_middlewares(self, config):
        self.add_middleware(GZipMiddleware, minimum_size=1024, compresslevel=7)

    def configure_application(self, config):
        ...

    @staticmethod
    def submit_task(*args, **kwargs):
        # raddus_task(args, kwargs)
        ...

    def load_configuration(self):
        return self.get_configuration()

    @classmethod
    def _configure_singleton(cls, *args, **kwargs):
        if cls.has_singleton_instance():
            cls.VM_DEFAULT.configure()

    @classmethod
    def get_default_instance(cls, *args, create_instance=True, **kwargs):
        if create_instance and not cls.has_singleton_instance():
            cls.get_class_locker().acquire()
            try:
                config = Configuration.get_default_instance()
                cls.VM_DEFAULT = object.__new__(cls)
                cls.VM_DEFAULT.__init__(*args, config=config, **kwargs)
                cls._configure_singleton()
            finally:
                cls.get_class_locker().release()
        return cls.VM_DEFAULT
