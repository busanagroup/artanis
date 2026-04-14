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
import asyncio
import logging
from pathlib import Path
import threading
import typing as t
import uuid

from artanis import injection, exceptions
from artanis.asgi import routing, http, types,  url
from artanis.asgi.auth import types as AccessTokenComponent, RefreshTokenComponent
from artanis.asgi.components import asgi, validation
from artanis.asgi.middlewares import  Middleware
from artanis.asgi.routing import WebSocketRoute
from artanis.config import Configuration
from artanis.entrypoint import artanis_monitor, artanis_startup, artanis_shutdown
from artanis.injection import Components
from artanis.resources import  ResourceRoute, resource as rsc
from artanis.asgi.asgibase import BaseASGIService
from artanis.asgi.auth import AccessTokenComponent, RefreshTokenComponent
from artanis.asgi.middlewares import Middleware, CORSMiddleware, GZipMiddleware
from artanis.config import Configuration
from artanis.entrypoint import artanis_monitor, artanis_startup, artanis_shutdown

logger = logging.getLogger(__name__)

__all__ = ["ASGIService"]

FRONTEND_TEMPLATES_PATH = Path(__file__).resolve().parent / "templates" / "frontend"
FRONTEND_CLIENT_PATH = FRONTEND_TEMPLATES_PATH
FRONTEND_ASSETS_PATH = FRONTEND_CLIENT_PATH / "assets"


class ASGIService(BaseASGIService):

    def __init__(
            self,
            config: Configuration | None = None,
            debug: bool = False,
            parent: ASGIService | None = None,
            schema_library: str | None = "pydantic",
    ):
        config: Configuration = config or Configuration.get_default_instance(create_instance=False)
        app_name = config.get_property_value(Configuration.ARTANIS_APP_NAME, '')
        openapi = {
            "info": {
                "title": app_name,
                "version": "0.1.0",
                "summary": f"{app_name} application",
                "description": "The future is ours",
            },
        }
        super().__init__(
            config=config,
            debug=debug,
            openapi=openapi,
            schema_library=schema_library,
            parent=parent
        )
        jwt_secret = config.get_property_value(config.JWT_SECRET_KEY, str(uuid.UUID(int=0)))
        components = [
            AccessTokenComponent(
                jwt_secret.encode(),
                header_prefix=config.get_property_value(config.JWT_HEADER_PREFIX),
                header_key=config.get_property_value(config.JWT_ACCESS_COOKIE_KEY),
                cookie_key=config.get_property_value(config.JWT_ACCESS_COOKIE_KEY)
            ),
            RefreshTokenComponent(
                jwt_secret.encode(),
                header_prefix=config.get_property_value(Configuration.JWT_HEADER_PREFIX),
                header_key=config.get_property_value(Configuration.JWT_REFRESH_COOKIE_KEY),
                cookie_key=config.get_property_value(Configuration.JWT_REFRESH_COOKIE_KEY)
            )
        ]
        self.add_component_set(components)

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
        self.events.startup += [mod.on_startup for mod in self.modules.values()]
        self.events.shutdown += [mod.on_shutdown for mod in self.modules.values()]

    def configure_middlewares(self, config):
        cors = config.get_property_value(config.ARTANIS_SECURITY_CORS_ORIGINS, '')
        self.add_middleware(Middleware(
            GZipMiddleware,
            minimum_size=2048,
            compresslevel=7,
        ))
        self.add_middleware(Middleware(
            CORSMiddleware,
            allow_origins=cors.split(','),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ))
        ...

    def configure_application(self, config):
        self.add_route("/assets/{filename}", self.frontend_asset, methods=["GET"], include_in_schema=False)
        self.add_route("/", self.frontend_view, methods=["GET"], include_in_schema=False)
            

    def configure_endpoints(self, config):
        ...

    def frontend_view(self) -> http.HTMLResponse:
        index_path = FRONTEND_CLIENT_PATH / "index.html"
        if not index_path.exists():
            raise exceptions.HTTPException(status_code=500, detail="Frontend index.html not found")

        return http.HTMLFileResponse(str(index_path))

    def frontend_asset(self, filename: str) -> http.FileResponse:
        return http.FileResponse(str(FRONTEND_ASSETS_PATH / filename))
    
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
