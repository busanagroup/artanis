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
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

from starlette.applications import P
from starlette.datastructures import State
from starlette.middleware import Middleware, _MiddlewareFactory
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.middleware.exceptions import ExceptionMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Router
from starlette.websockets import WebSocket
from starlette.types import ASGIApp, ExceptionHandler, Receive, Scope, Send

from artanis.abc.objloader import ObjectLoader
from artanis.abc.objlock import SyncLock
from artanis.abc.service import StartableService
from artanis.abc.singleton import Singleton
from artanis.asgi.exceptions import exception_handlers
from artanis.asgi.middleware.asyncexitstack import AsyncExitStackMiddleware
from artanis.config import Configuration
from artanis.entrypoint import artanis_monitor, artanis_startup, artanis_shutdown


@dataclass
class OpenAPISpec:
    title: str = "Artanis"
    version: str  = "0.1.0"
    openapi_version: str = "3.1.0"
    summary: str | None = None
    description: str | None = None
    terms_of_service: str | None = None
    contact: dict[str, str | Any] | None = None
    license_info: dict[str, str | Any] | None = None
    routes: Router | None = None
    webhooks: Router | None = None
    tags: str = None
    servers: list = field(default_factory=list)
    separate_input_output_schemas: bool = True
    external_docs: dict[str, Any | None] = None
    openapi_url: str | None = "/openapi.json"
    docs_url: str | None = "/docs"
    swagger_ui_oauth2_redirect_url: str = "/docs/oauth2-redirect"
    swagger_ui_parameters: dict[str, Any | None] = None
    swagger_ui_init_oauth: dict[str, Any | None] = None


class ASGIService(StartableService, Singleton, SyncLock, ObjectLoader):

    def __init__(self, *args, root_path: str = "", debug: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_path = root_path
        self.debug = debug
        self.state = State()
        self.router = Router()
        self.exception_handlers = exception_handlers
        self.user_middleware = []
        self.middleware_stack: ASGIApp | None = None
        self.openapi_specs: OpenAPISpec = kwargs.pop('openapi_specs') if 'openapi_specs' in kwargs else OpenAPISpec()

    def configure_lifespan(self, config):
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

    def configure_modules(self, config):
        ...

    def configure_services(self, config):
        ...

    def configure_middlewares(self, config):
        ...

    def configure_application(self, config):
        ...

    def configure_endpoints(self, config):
        ...

    def do_configure(self):
        super().do_configure()
        config = self.get_configuration()
        self.configure_lifespan(config)
        self.configure_modules(config)
        self.configure_services(config)
        self.configure_middlewares(config)
        self.configure_application(config)
        self.configure_endpoints(config)
        if self.middleware_stack is None:
            self.middleware_stack = self.build_middleware_stack()

    def add_event_handler(
            self,
            event_type: str,
            func: Callable,  # type: ignore[type-arg]
    ) -> None:  # pragma: no cover
        self.router.add_event_handler(event_type, func)

    def add_route(
            self,
            path: str,
            route: Callable[[Request], Awaitable[Response] | Response],
            methods: list[str] | None = None,
            name: str | None = None,
            include_in_schema: bool = True,
    ) -> None:  # pragma: no cover
        self.router.add_route(path, route, methods=methods, name=name, include_in_schema=include_in_schema)

    def add_websocket_route(
            self,
            path: str,
            route: Callable[[WebSocket], Awaitable[None]],
            name: str | None = None,
    ) -> None:  # pragma: no cover
        self.router.add_websocket_route(path, route, name=name)

    def add_middleware(
            self,
            middleware_class: _MiddlewareFactory[P],
            *args: P.args,
            **kwargs: P.kwargs,
    ) -> None:
        if self.middleware_stack is not None:  # pragma: no cover
            raise RuntimeError("Cannot add middleware after an application has started")
        self.user_middleware.insert(0, Middleware(middleware_class, *args, **kwargs))

    def mount(self, path: str, app: ASGIApp, name: str | None = None) -> None:
        self.router.mount(path, app=app, name=name)  # pragma: no cover

    def host(self, host: str, app: ASGIApp, name: str | None = None) -> None:
        self.router.host(host, app=app, name=name)  # pragma: no cover

    def build_middleware_stack(self) -> ASGIApp:
        debug = self.debug
        error_handler = None
        _exception_handlers: dict[Any, ExceptionHandler] = {}

        for key, value in self.exception_handlers.items():
            if key in (500, Exception):
                error_handler = value
            else:
                _exception_handlers[key] = value

        middleware = (
                [Middleware(ServerErrorMiddleware, handler=error_handler, debug=debug),
                 Middleware(GZipMiddleware, minimum_size=1024, compresslevel=7)]
                + self.user_middleware
                + [
                    Middleware(
                        ExceptionMiddleware, handlers=_exception_handlers, debug=debug
                    ),
                    Middleware(AsyncExitStackMiddleware),
                ]
        )

        app = self.router
        for cls, args, kwargs in reversed(middleware):
            app = cls(app, *args, **kwargs)
        return app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        scope["app"] = self
        if self.root_path:
            scope["root_path"] = self.root_path
        if self.middleware_stack is None:
            self.middleware_stack = self.build_middleware_stack()
        await self.middleware_stack(scope, receive, send)

    @classmethod
    def _configure_singleton(cls):
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
