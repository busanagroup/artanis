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
from typing import Any

from starlette.middleware import Middleware
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.middleware.exceptions import ExceptionMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.types import ASGIApp, ExceptionHandler, Scope, Send, Receive

from artanis import injection
from artanis.abc.components import WorkerComponent
from artanis.asgi.events import Events
from artanis.asgi.middlewares import MiddlewareStack
from artanis.asgi.modules import Modules
from artanis.asgi.pagination import paginator
from artanis.asgi.schemas.modules import SchemaModule
from artanis.injection import injector
from artanis.abc.objloader import ObjectLoader
from artanis.abc.objlock import SyncLock
from artanis.abc.service import StartableService
from artanis.abc.singleton import Singleton
from artanis.asgi.middleware.asyncexitstack import AsyncExitStackMiddleware
from artanis.config import Configuration
from artanis.entrypoint import artanis_monitor, artanis_startup, artanis_shutdown
from artanis.asgi.exceptions import exception_handlers
from artanis.asgi import routing, http, types, websockets
from artanis.models import ModelsModule
from artanis.resources import ResourcesModule
from artanis.resources.workers import ResourceWorker


class ASGIService(StartableService, Singleton, SyncLock, ObjectLoader):

    resources: ResourcesModule
    schema: SchemaModule
    models: ModelsModule

    def __init__(
            self,
            config: Any = None,
            debug: bool = False,
            parent: ASGIService | None = None
    ):
        super().__init__(config=config)
        openapi: types.OpenAPISpec = {
            "info": {
                "title": "Artanis",
                "version": "0.1.0",
                "summary": "Artanis application",
                "description": "The future is ours",
            },
        }
        self.debug = debug
        self.exception_handlers = exception_handlers
        self.parent = parent
        self._shutdown = False

        self._injector = injector.Injector(Context)

        default_components = []

        if (worker := ResourceWorker() if ResourceWorker else None) and WorkerComponent:
            default_components.append(WorkerComponent(worker=worker))

        default_modules = [
            ResourcesModule(worker=worker),
            SchemaModule(openapi, schema="/schema/", docs="/docs/"),
            ModelsModule(),
        ]
        self.modules = Modules(app=self, modules={*default_modules, *([])})

        self.app = self.router = routing.Router(
            routes=None, components=[*default_components, *([])], lifespan=None, app=self
        )
        self.middleware = MiddlewareStack(app=self, middleware=[], debug=debug)
        self.schema.schema_library = None
        self.schema.add_routes()
        self.events = Events.build(**({}))
        self.events.startup += [m.on_startup for m in self.modules.values()]
        self.events.shutdown += [m.on_shutdown for m in self.modules.values()]
        self.paginator = paginator

    def do_configure(self):
        super().do_configure()
        config = self.get_configuration()

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
            await artanis_startup(config)
            await self.start()

        async def process_shutdown():
            await self.stop()
            await artanis_shutdown(config)

        self.add_event_handler("startup", process_startup)
        self.add_event_handler("shutdown", process_shutdown)
        self.configure_modules(config)
        self.configure_services(config)
        self.configure_middlewares(config)
        self.configure_application(config)

    def add_event_handler(self, event_type: str, func: Callable) -> None:
        raise NotImplementedError

    def configure_modules(self, config):
        ...

    def configure_services(self, config):
        ...

    def configure_middlewares(self, config):
        ...

    def configure_application(self, config):
        ...

    def load_configuration(self):
        return self.get_configuration()

    def build_middleware_stack(self) -> ASGIApp:
        debug = self.debug
        error_handler = None
        exception_handlers: dict[Any, ExceptionHandler] = {}

        for key, value in self.exception_handlers.items():
            if key in (500, Exception):
                error_handler = value
            else:
                exception_handlers[key] = value

        middleware = (
                [Middleware(ServerErrorMiddleware, handler=error_handler, debug=debug),
                 Middleware(GZipMiddleware, minimum_size=1024, compresslevel=7)]
                + self.user_middleware
                + [
                    Middleware(
                        ExceptionMiddleware, handlers=exception_handlers, debug=debug
                    ),
                    Middleware(AsyncExitStackMiddleware),
                ]
        )

        app = self.router
        for cls, args, kwargs in reversed(middleware):
            app = cls(app, *args, **kwargs)
        return app

    @classmethod
    def _configure_singleton(cls, *args, **kwargs):
        if cls.has_singleton_instance():
            cls.VM_DEFAULT.configure()

    @classmethod
    def get_default_instance(cls, *args, create_instance=True, **kwargs):
        if create_instance and not cls.has_singleton_instance():
            cls.get_class_locker().acquire()
            try:
                config = Configuration.get_default_instance(create_instance=False)
                cls.VM_DEFAULT = cls(*args, config=config, **kwargs)
                cls._configure_singleton()
            finally:
                cls.get_class_locker().release()
        return cls.VM_DEFAULT


class Context(injection.Context):
    types = {
        "scope": types.Scope,
        "receive": types.Receive,
        "send": types.Send,
        "exc": Exception,
        "app": ASGIService,
        "route": routing.BaseRoute,
        "request": http.Request,
        "response": http.Response,
        "websocket": websockets.WebSocket,
        "websocket_message": types.Message,
        "websocket_encoding": types.Encoding,
        "websocket_code": types.Code,
    }

    hashable = (
        "scope",
        "receive",
        "send",
        "exc",
        "app",
        "route",
        "response",
        "websocket_message",
        "websocket_encoding",
        "websocket_code",
    )
