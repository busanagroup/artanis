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

import msgspec
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.middleware.exceptions import ExceptionMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Router
from starlette.types import ASGIApp, ExceptionHandler

from artanis.abc.objloader import ObjectLoader
from artanis.abc.objlock import SyncLock
from artanis.abc.service import StartableService
from artanis.abc.singleton import Singleton
from artanis.asgi.exceptions import exception_handlers
from artanis.asgi.middleware.asyncexitstack import AsyncExitStackMiddleware
from artanis.asgi.swagger.docs import get_swagger_ui_oauth2_redirect_html, get_swagger_ui_html
from artanis.config import Configuration
from artanis.entrypoint import artanis_monitor, artanis_startup, artanis_shutdown


class OpenAPISpec(msgspec.Struct):
    title: str | None = "Artanis"
    version: str | None = None
    openapi_version: str | None = None
    summary: str | None = None
    description: str | None = None
    terms_of_service: str | None = None
    contact: str | None = None
    license_info: str | None = None
    routes: Router | None = None
    webhooks: Router | None = None
    tags: str = None
    servers: list = []
    separate_input_output_schemas: bool = True
    external_docs: dict[str, Any | None] = None
    openapi_url: str | None = "/openapi.json"
    docs_url: str | None = "/docs"
    swagger_ui_oauth2_redirect_url: str | None = "/docs/oauth2-redirect"
    swagger_ui_parameters: dict[str, Any | None] = None
    swagger_ui_init_oauth: dict[str, Any | None] = None


class ASGIService(StartableService, Singleton, SyncLock, ObjectLoader):

    def do_configure(self):
        super(ASGIService, self).do_configure()
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
            await self.start()
            await artanis_startup(config)

        async def process_shutdown():
            await artanis_shutdown(config)
            await self.stop()

        self.configure_modules(config)
        self.configure_services(config)
        self.configure_middlewares(config)
        self.configure_application(config)
        self.add_event_handler("startup", process_startup)
        self.add_event_handler("shutdown", process_shutdown)

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


class ASGIFastAPI(FastAPI, ASGIService):

    def __init__(self, *args, **kwargs):
        config = kwargs.pop('config')
        super(ASGIFastAPI, self).__init__(*args, exception_handlers=exception_handlers, **kwargs)
        for base in ASGIService.__bases__:
            if base is not FastAPI:
                base.__init__(self, *args, config=config, **kwargs)

    def do_configure(self):
        super().do_configure()
        if self.middleware_stack is None:
            self.middleware_stack = self.build_middleware_stack()

    def build_middleware_stack(self) -> ASGIApp:
        # Duplicate/override from Starlette to add AsyncExitStackMiddleware
        # inside of ExceptionMiddleware, inside of custom user middlewares
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


class ASGIStarlette(Starlette, ASGIService):

    def __init__(self, *args, **kwargs) -> None:
        self.root_path: str = ""
        self.openapi_schema: dict[str, Any] | None = None
        self.openapi_specs = kwargs.pop('openapi_specs') if 'openapi_specs' in kwargs else OpenAPISpec()
        config: Configuration = kwargs.pop('config')
        super().__init__(*args, exception_handlers=exception_handlers, **kwargs)
        for base in ASGIService.__bases__:
            if base is not Starlette:
                base.__init__(self, *args, config=config, **kwargs)

    def setup_openapi(self) -> None:
        async def openapi(request: Request) -> JSONResponse:
            root_path = request.scope.get('root_path', '').rstrip('/')
            schema = self.openapi()
            if root_path:
                server_urls = {s.get("url") for s in schema.get("servers", [])}
                if root_path not in server_urls:
                    schema = dict(schema)
                    schema['servers'] = [{"url": root_path}] + schema.get("servers", [])
            return JSONResponse(schema)

        async def swagger_ui_html(req: Request) -> HTMLResponse:
            root_path = req.scope.get("root_path", "").rstrip("/")
            openapi_url = root_path + self.openapi_specs.openapi_url
            oauth2_redirect_url = self.openapi_specs.swagger_ui_oauth2_redirect_url
            if oauth2_redirect_url:
                oauth2_redirect_url = root_path + oauth2_redirect_url
            return get_swagger_ui_html(
                openapi_url=openapi_url,
                title=f"{self.openapi_specs.title} - Swagger UI",
                oauth2_redirect_url=oauth2_redirect_url,
                init_oauth=self.openapi_specs.swagger_ui_init_oauth,
                swagger_ui_parameters=self.openapi_specs.swagger_ui_parameters,
            )

        async def swagger_ui_redirect(req: Request) -> HTMLResponse:
            return get_swagger_ui_oauth2_redirect_html()

        self.add_route(self.openapi_specs.openapi_url, openapi)
        self.add_route(self.openapi_specs.docs_url, swagger_ui_html, include_in_schema=False)
        if self.openapi_specs.swagger_ui_oauth2_redirect_url:
            self.add_route(
                self.openapi_specs.swagger_ui_oauth2_redirect_url,
                swagger_ui_redirect,
                include_in_schema=False,
            )

    def openapi(self) -> dict[str, Any]:
        if not self.openapi_schema:
            self.openapi_schema = get_openapi(
                title=self.openapi_specs.title,
                version=self.openapi_specs.version,
                openapi_version=self.openapi_specs.openapi_version,
                summary=self.openapi_specs.summary,
                description=self.openapi_specs.description,
                terms_of_service=self.openapi_specs.terms_of_service,
                contact=self.openapi_specs.contact,
                license_info=self.openapi_specs.license_info,
                routes=self.routes,
                servers=self.openapi_specs.servers,
                separate_input_output_schemas=self.openapi_specs.separate_input_output_schemas,
            )
        return self.openapi_schema

    def do_configure(self):
        self.setup_openapi()
        super().do_configure()
        if self.middleware_stack is None:
            self.middleware_stack = self.build_middleware_stack()

    def build_middleware_stack(self) -> ASGIApp:
        # Duplicate/override from Starlette to add AsyncExitStackMiddleware
        # inside of ExceptionMiddleware, inside of custom user middlewares
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

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if self.root_path:
            scope["root_path"] = self.root_path
        await super().__call__(scope, receive, send)
