#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Busana Apparel Group. All rights reserved.
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
import functools
import typing as t

from artanis import injection, exceptions
from artanis.abc.objloader import ObjectLoader
from artanis.abc.objlock import SyncLock
from artanis.abc.service import StartableService
from artanis.abc.singleton import Singleton
from artanis.asgi import types, routing, http, websockets
from artanis.asgi.events import Events
from artanis.asgi.middlewares import MiddlewareStack
from artanis.asgi.pagination import paginator
from artanis.asgi.routing import WebSocketRoute
from artanis.asgi.schemas.modules import SchemaModule
from artanis.config import Configuration
from artanis.ddd import WorkerComponent
from artanis.injection import injector
from artanis.models import ModelsModule
from artanis.modules import Modules, Module
from artanis.resources import ResourcesModule, ResourceRoute, resource as rsc
from artanis.resources.workers import ResourceWorker
from artanis.sqlentity.module import SQLAlchemyModule

if t.TYPE_CHECKING:
    from artanis.asgi.middlewares import Middleware


class BaseASGIService(StartableService, Singleton, SyncLock, ObjectLoader):
    resources: ResourcesModule
    schema: SchemaModule
    models: ModelsModule
    sqlalchemy: SQLAlchemyModule

    def __init__(
            self,
            config: Configuration = None,
            debug: bool = False,
            parent: BaseASGIService | None = None,
            openapi: types.OpenAPISpec | dict | None = None,
            schema_library: str | None = "pydantic",
    ):
        super().__init__(config=config)
        self.debug = debug
        self.exception_handlers = None  # exception_handlers
        self.parent = parent
        self._shutdown = False
        self._status = types.AppStatus.NOT_STARTED

        self._injector = injector.Injector(Context)

        default_components = []
        if (worker := ResourceWorker() if ResourceWorker else None) and WorkerComponent:
            default_components.append(WorkerComponent(worker=worker))

        openapi = openapi or {
                "info": {
                    "title": "Artanis",
                    "version": "0.1.0",
                    "summary": "Artanis application",
                    "description": "The future is ours",
                },
            }

        default_modules = [
            ResourcesModule(worker=worker),
            SchemaModule(openapi, schema="/openapi.json", docs="/docs"),
            ModelsModule(),
            SQLAlchemyModule(config, single_connection=True),
        ]
        self.modules = Modules(app=self, modules=default_modules)
        self.app = self.router = routing.Router(components=default_components, app=self)
        self.middleware = MiddlewareStack(app=self, middleware=[], debug=debug)
        self.schema.schema_library = schema_library
        self.schema.add_routes()
        self.events = Events.build()
        self.paginator = paginator

    def do_configure(self):
        super().do_configure()
        config = self.get_configuration()
        self.configure_lifespan(config)
        self.configure_modules(config)
        self.configure_services(config)
        self.configure_middlewares(config)
        self.configure_application(config)
        self.configure_endpoints(config)

    def configure_lifespan(self, config):
        ...

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

    @property
    def status(self) -> types.AppStatus:
        return self._status

    @status.setter
    def status(self, s: types.AppStatus) -> None:
        self.get_lock()
        with self.threading_lock():
            self._status = s

    @property
    def components(self) -> injection.Components:
        return injection.Components(self.router.components + (self.parent.components if self.parent else ()))

    def add_component(self, component: injection.Component):
        self.router.add_component(component)

    def add_component_set(self, components: set[injection.Component]):
        self.router.add_component_set(components)

    @property
    def routes(self) -> list[routing.BaseRoute]:
        return self.router.routes

    @property
    def injector(self) -> injection.Injector:
        components = injection.Components(self.components + asgi.ASGI_COMPONENTS + validation.VALIDATION_COMPONENTS)
        if self._injector.components != components:
            self._injector.components = components
        return self._injector

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

    def add_module(self, module: Module):
        self.modules.add_module(self, module)

    def add_exception_handler(
            self,
            exc_class_or_status_code: int | type[Exception],
            handler: t.Callable
    ):
        self.middleware.add_exception_handler(exc_class_or_status_code, handler)

    def add_event_handler(self, event: str, func: t.Callable) -> None:
        self.events.register(event, func)

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

    def route(
            self,
            path: str,
            methods: list[str] | None = None,
            *,
            name: str | None = None,
            include_in_schema: bool = True,
            pagination: types.Pagination | None = None,
            tags: dict[str, t.Any] | None = None,
    ) -> t.Callable[[types.HTTPHandler], types.HTTPHandler]:
        return self.router.route(
            path, methods=methods, name=name, include_in_schema=include_in_schema, pagination=pagination, tags=tags
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

    def __getattr__(self, item: str) -> t.Any:
        try:
            return self.modules.__getitem__(item)
        except KeyError:
            return None  # type: ignore[return-value]

    async def __call__(self, scope: types.Scope, receive: types.Receive, send: types.Send) -> None:
        if scope["type"] != "lifespan":
            if self.status in (types.AppStatus.NOT_STARTED, types.AppStatus.STARTING):
                raise exceptions.ApplicationError("Application is not ready to process requests yet.")

            elif self.status in (types.AppStatus.SHUT_DOWN, types.AppStatus.SHUTTING_DOWN):
                raise exceptions.ApplicationError("Application is already shut down.")

        scope["app"] = self
        scope.setdefault("root_app", self)
        await self.middleware(scope, receive, send)

    get = functools.partialmethod(route, methods=["GET"])
    head = functools.partialmethod(route, methods=["HEAD"])
    post = functools.partialmethod(route, methods=["POST"])
    put = functools.partialmethod(route, methods=["PUT"])
    delete = functools.partialmethod(route, methods=["DELETE"])
    connect = functools.partialmethod(route, methods=["CONNECT"])
    options = functools.partialmethod(route, methods=["OPTIONS"])
    trace = functools.partialmethod(route, methods=["TRACE"])
    patch = functools.partialmethod(route, methods=["PATCH"])
    add_get = functools.partialmethod(add_route, methods=["GET"])
    add_head = functools.partialmethod(add_route, methods=["HEAD"])
    add_post = functools.partialmethod(add_route, methods=["POST"])
    add_put = functools.partialmethod(add_route, methods=["PUT"])
    add_delete = functools.partialmethod(add_route, methods=["DELETE"])
    add_connect = functools.partialmethod(add_route, methods=["CONNECT"])
    add_options = functools.partialmethod(add_route, methods=["OPTIONS"])
    add_trace = functools.partialmethod(add_route, methods=["TRACE"])
    add_patch = functools.partialmethod(add_route, methods=["PATCH"])

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
        "app": BaseASGIService,
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
