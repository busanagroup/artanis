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
import logging
import threading
import typing as t
import uuid

from artanis import injection, exceptions
from artanis.abc.components import WorkerComponent
from artanis.abc.objloader import ObjectLoader
from artanis.abc.objlock import SyncLock
from artanis.abc.service import StartableService
from artanis.abc.singleton import Singleton
from artanis.asgi import routing, http, types, websockets, url
from artanis.asgi.auth import AccessTokenComponent, RefreshTokenComponent, AuthenticationMiddleware
from artanis.asgi.components import asgi, validation
from artanis.asgi.events import Events
from artanis.asgi.exceptions import exception_handlers
from artanis.asgi.middlewares import MiddlewareStack, Middleware
from artanis.asgi.modules import Modules
from artanis.asgi.pagination import paginator
from artanis.asgi.routing import WebSocketRoute
from artanis.asgi.schemas.modules import SchemaModule
from artanis.config import Configuration
from artanis.entrypoint import artanis_monitor, artanis_startup, artanis_shutdown
from artanis.injection import injector, Components
from artanis.models import ModelsModule
from artanis.resources import ResourcesModule, ResourceRoute, resource as rsc
from artanis.resources.workers import ResourceWorker

logger = logging.getLogger(__name__)


class ASGIService(StartableService, Singleton, SyncLock, ObjectLoader):
    resources: ResourcesModule
    schema: SchemaModule
    models: ModelsModule

    def __init__(
            self,
            config: Configuration = None,
            debug: bool = False,
            parent: ASGIService | None = None,
            openapi: types.OpenAPISpec = {
                "info": {
                    "title": "Artanis",
                    "version": "0.1.0",
                    "summary": "Artanis application",
                    "description": "The future is ours",
                },
            },
    ):
        super().__init__(config=config)
        self.debug = debug
        self.exception_handlers = exception_handlers
        self.parent = parent
        self._shutdown = False
        self._status = types.AppStatus.NOT_STARTED

        self._injector = injector.Injector(Context)

        default_components = []

        if (worker := ResourceWorker() if ResourceWorker else None) and WorkerComponent:
            default_components.append(WorkerComponent(worker=worker))

        default_modules = [
            ResourcesModule(worker=worker),
            SchemaModule(openapi, schema="/openapi.json", docs="/docs/"),
            ModelsModule(),
        ]
        self.modules = Modules(app=self, modules={*default_modules, *([])})

        jwt_secret = config.get_property_value(config.JWT_SECRET_KEY, str(uuid.UUID(int=0)))
        self.app = self.router = routing.Router(
            routes=None, components=[*default_components, *(
                [
                    AccessTokenComponent(
                        jwt_secret.encode(),
                        header_prefix=config.get_property_value(config.JWT_HEADER_PREFIX),
                        header_key=config.get_property_value(config.JWT_ACCESS_COOKIE_KEY),
                        cookie_key=config.get_property_value(config.JWT_ACCESS_COOKIE_KEY)
                    ),
                    RefreshTokenComponent(
                        jwt_secret.encode(),
                        header_prefix=config.get_property_value(config.JWT_HEADER_PREFIX),
                        header_key=config.get_property_value(config.JWT_REFRESH_COOKIE_KEY),
                        cookie_key=config.get_property_value(config.JWT_REFRESH_COOKIE_KEY)
                    )
                ])], lifespan=None, app=self
        )
        self.middleware = MiddlewareStack(
            app=self,
            middleware=[
                Middleware(AuthenticationMiddleware)
            ],
            debug=debug
        )
        self.schema.schema_library = None
        self.schema.add_routes()
        self.events = Events.build(**({}))
        self.events.startup += [mod.on_startup for mod in self.modules.values()]
        self.events.shutdown += [mod.on_shutdown for mod in self.modules.values()]
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
        self.configure_endpoints(config)

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

    def load_configuration(self):
        return self.get_configuration()

    def __getattr__(self, item: str) -> t.Any:
        try:
            return self.modules.__getitem__(item)
        except KeyError:
            return None

    @property
    def status(self) -> types.AppStatus:
        return self._status

    @status.setter
    def status(self, s: types.AppStatus) -> None:
        logger.debug("Transitioning %s from %s to %s", self, self._status, s)

        with threading.Lock():
            self._status = s

    @property
    def components(self) -> injection.Components:
        return Components(self.router.components + (self.parent.components if self.parent else ()))

    def add_component(self, component: injection.Component):
        self.router.add_component(component)

    @property
    def routes(self) -> list[routing.BaseRoute]:
        return self.router.routes

    def add_route(
            self,
            path: str | None = None,
            endpoint: types.HTTPHandler | None = None,
            methods: list[str] | None = None,
            *,
            name: str | None = None,
            include_in_schema: bool = True,
            route: routing.Route | None = None,
            pagination: types.Pagination | None = None,
            tags: dict[str, t.Any] | None = None,
    ) -> routing.Route:
        return self.router.add_route(
            path,
            endpoint,
            methods=methods,
            name=name,
            include_in_schema=include_in_schema,
            route=route,
            pagination=pagination,
            tags=tags,
        )

    def add_websocket_route(
            self,
            path: str | None = None,
            endpoint: types.WebSocketHandler | None = None,
            *,
            name: str | None = None,
            route: WebSocketRoute | None = None,
            pagination: types.Pagination | None = None,
            tags: dict[str, t.Any] | None = None,
    ) -> WebSocketRoute:
        return self.router.add_websocket_route(
            path,
            endpoint,
            name=name,
            route=route,
            pagination=pagination,
            tags=tags
        )

    def add_exception_handler(
            self,
            exc_class_or_status_code: int | type[Exception],
            handler: t.Callable
    ):
        self.middleware.add_exception_handler(exc_class_or_status_code, handler)

    def add_middleware(
            self,
            middleware: "Middleware"
    ):
        self.middleware.add_middleware(middleware)

    def add_resource(
            self,
            path: str,
            resource: rsc.Resource | type[rsc.Resource],
            *args,
            include_in_schema: bool = True,
            tags: dict[str, dict[str, t.Any]] | None = None,
            **kwargs,
    ) -> ResourceRoute:
        return self.resources.add_resource(
            path,
            resource,
            *args,
            include_in_schema=include_in_schema,
            tags=tags,
            **kwargs
        )

    def mount(
            self,
            path: str | None = None,
            app: types.App | None = None,
            *,
            name: str | None = None,
            mount: routing.Mount | None = None,
            tags: dict[str, t.Any] | None = None,
    ) -> routing.Mount:
        return self.router.mount(path, app, name=name, mount=mount, tags=tags)

    def resolve_route(self, scope: types.Scope) -> tuple[routing.BaseRoute, types.Scope]:
        return self.router.resolve_route(scope)

    def resolve_url(self, name: str, **path_params: t.Any) -> url.URL:
        return self.router.resolve_url(name, **path_params)

    async def __call__(self, scope: types.Scope, receive: types.Receive, send: types.Send) -> None:
        if scope["type"] != "lifespan":
            if self.status in (types.AppStatus.NOT_STARTED, types.AppStatus.STARTING):
                raise exceptions.ApplicationError("Application is not ready to process requests yet.")

            elif self.status in (types.AppStatus.SHUT_DOWN, types.AppStatus.SHUTTING_DOWN):
                raise exceptions.ApplicationError("Application is already shut down.")

        scope["app"] = self
        scope.setdefault("root_app", self)
        await self.middleware(scope, receive, send)

    def add_event_handler(self, event: str, func: t.Callable) -> None:
        self.events.register(event, func)

    @property
    def injector(self) -> injection.Injector:
        components = injection.Components(self.components + asgi.ASGI_COMPONENTS + validation.VALIDATION_COMPONENTS)
        if self._injector.components != components:
            self._injector.components = components
        return self._injector

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
