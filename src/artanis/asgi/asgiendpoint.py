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

import functools

from collections.abc import Collection
from dataclasses import field, dataclass
from enum import Enum
from pathlib import PurePosixPath
from re import Pattern
from typing import Any, Callable, Awaitable

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, Response, RedirectResponse
from starlette.routing import Router, Match, compile_path, BaseRoute, Mount, Route
from starlette._exception_handler import wrap_app_handling_exceptions
from starlette.staticfiles import StaticFiles
from starlette.types import ASGIApp, Scope, Send, Receive
from starlette.websockets import WebSocketClose

from artanis.abc.configurable import Configurable
from artanis.abc.service import StartableService
from artanis.abc.startable import StartableListener
from artanis.datastructures import Default, URL, DefaultPlaceholder
from artanis.utils import get_route_path, import_function, get_name, is_async_callable


class Handled(Enum):
    NONE = 0
    PARTIAL = 1
    FULL = 2


@dataclass
class OpenAPISpec:
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
    servers: list = field(default_factory=list)
    separate_input_output_schemas: bool = True
    external_docs: dict[str, Any | None] = None
    openapi_url: str | None = "/openapi.json"
    docs_url: str | None = "/docs"
    swagger_ui_oauth2_redirect_url: str | None = "/docs/oauth2-redirect"
    swagger_ui_parameters: dict[str, Any | None] = None
    swagger_ui_init_oauth: dict[str, Any | None] = None


class Descriptor:
    name: str
    path: str
    path_regex: Any
    path_format: Any
    param_convertors: Any
    handle_request: bool = False

    def describe(self, name):
        self.name = name
        self.path = f"/{self.name}"
        self.path_regex, self.path_format, self.param_convertors = compile_path(self.path + "/{path:path}")

    def matches(self, scope: Scope) -> tuple[Match, Scope]:
        path_params: dict[str, Any]
        if scope["type"] == "http":  # pragma: no branch
            root_path = scope.get("root_path", "")
            route_path = get_route_path(scope)
            match = self.path_regex.match(route_path)
            if match:
                matched_params = match.groupdict()
                for key, value in matched_params.items():
                    matched_params[key] = self.param_convertors[key].convert(value)
                remaining_path = "/" + matched_params.pop("path")
                matched_path = route_path[: -len(remaining_path)]
                path_params = dict(scope.get("path_params", {}))
                path_params.update(matched_params)
                child_scope = {
                    "path_params": path_params,
                    "app_root_path": scope.get("app_root_path", root_path),
                    "root_path": root_path + matched_path,
                }
                return Match.FULL, child_scope
        return Match.NONE, {}


class ControllerABC(Configurable):
    descriptor: Descriptor

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_published_methods = hasattr(self, "published_methods")

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        published_methods = [func for service, func in cls.__dict__.items() if hasattr(func, "published")]
        if published_methods:
            cls.published_methods = published_methods
        if hasattr(cls, "descriptor"):
            cls.descriptor.describe(cls.__name__)


def request_response(
        func: Callable[[Request], Awaitable[Response] | Response],
) -> ASGIApp:
    """
    Takes a function or coroutine `func(request) -> response`,
    and returns an ASGI application.
    """
    f: Callable[[Request], Awaitable[Response]] = (
        func if is_async_callable(func) else functools.partial(run_in_threadpool, func)
    )

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope, receive, send)

        async def app(scope: Scope, receive: Receive, send: Send) -> None:
            response = await f(request)
            await response(scope, receive, send)

        await wrap_app_handling_exceptions(app, request)(scope, receive, send)

    return app


@dataclass
class Published:
    path: str = None
    response_model: Any = None
    status_code: int | None = None
    tags: list[str | Enum] | None = None
    summary: str | None = None
    description: str | None = None
    response_description: str = "Successful Response"
    responses: dict[int | str, dict[str, Any]] | None = None
    deprecated: bool | None = None
    name: str | None = None
    methods: set[str] | list[str] | None = None
    operation_id: str | None = None
    include_in_schema: bool = True
    response_class: type[Response] | DefaultPlaceholder = None
    dependency_overrides_provider: Any | None = None
    callbacks: list[BaseRoute] | None = None
    openapi_extra: dict[str, Any] | None = None
    strict_content_type: bool | DefaultPlaceholder = True
    path_regex: Pattern[str] | None = None
    path_format: str | None = None
    param_convertors: dict | None = None

    def __post_init__(self):
        self.path = f"/{self.name}" if self.path is None else self.path
        self.path_regex, self.path_format, self.param_convertors = compile_path(self.path)

    def matches(self, scope: Scope) -> tuple[Match, Scope]:
        path_params: dict[str, Any]
        if scope["type"] == "http":
            route_path = get_route_path(scope)
            match = self.path_regex.match(route_path)
            if match:
                matched_params = match.groupdict()
                for key, value in matched_params.items():
                    matched_params[key] = self.param_convertors[key].convert(value)
                path_params = dict(scope.get("path_params", {}))
                path_params.update(matched_params)
                child_scope = {"path_params": path_params}
                if self.methods and scope["method"] not in self.methods:
                    return Match.PARTIAL, child_scope
                else:
                    return Match.FULL, child_scope
        return Match.NONE, {}

    @staticmethod
    def prepare_endpoint(endpoint: Callable[..., Any]) -> Callable[..., Any]:
        endpoint_handler = endpoint
        while isinstance(endpoint_handler, functools.partial):
            endpoint_handler = endpoint_handler.func
        return request_response(endpoint)

    async def handle(self, scope: Scope, receive: Receive, send: Send):
        if self.methods and scope["method"] not in self.methods:
            headers = {"Allow": ", ".join(self.methods)}
            if "app" in scope:
                raise HTTPException(status_code=405, headers=headers)
            else:
                response = PlainTextResponse("Method Not Allowed", status_code=405, headers=headers)
            await response(scope, receive, send)
        else:
            endpoint = scope.get("endpoint")
            app = self.prepare_endpoint(endpoint)
            await app(scope, receive, send)


def published(
        func: Callable[..., Any] | None = None,
        path: str = None,
        response_model: Any = Default(None),
        status_code: int | None = None,
        tags: list[str | Enum] | None = None,
        summary: str | None = None,
        description: str | None = None,
        response_description: str = "Successful Response",
        responses: dict[int | str, dict[str, Any]] | None = None,
        deprecated: bool | None = None,
        name: str | None = None,
        methods: set[str] | list[str] | None = ("GET",),
        operation_id: str | None = None,
        include_in_schema: bool = True,
        response_class: type[Response] | DefaultPlaceholder = Default(JSONResponse),
        dependency_overrides_provider: Any | None = None,
        callbacks: list[BaseRoute] | None = None,
        openapi_extra: dict[str, Any] | None = None,
        strict_content_type: bool | DefaultPlaceholder = Default(True)
) -> Callable[..., Any]:
    if func:
        _name = get_name(func)
        func.published = Published(
            path=path,
            response_model=response_model,
            status_code=status_code,
            tags=tags,
            summary=summary,
            description=description,
            response_description=response_description,
            responses=responses,
            deprecated=deprecated,
            name=_name if name is None else name,
            methods=methods,
            operation_id=operation_id,
            include_in_schema=include_in_schema,
            response_class=response_class,
            dependency_overrides_provider=dependency_overrides_provider,
            callbacks=callbacks,
            openapi_extra=openapi_extra,
            strict_content_type=strict_content_type,
        )
        return func
    else:
        def wrapper(fnc):
            _name = get_name(fnc)
            fnc.published = Published(
                path=path,
                response_model=response_model,
                status_code=status_code,
                tags=tags,
                summary=summary,
                description=description,
                response_description=response_description,
                responses=responses,
                deprecated=deprecated,
                name=_name if name is None else name,
                methods=methods,
                operation_id=operation_id,
                include_in_schema=include_in_schema,
                response_class=response_class,
                dependency_overrides_provider=dependency_overrides_provider,
                callbacks=callbacks,
                openapi_extra=openapi_extra,
                strict_content_type=strict_content_type,
            )
            return fnc

        return wrapper


class ASGIEndPoint(ControllerABC):
    base_modules: str = None

    def __init__(self, *args, **kwargs):
        parent: StartableService = kwargs.pop('parent') if 'parent' in kwargs else None
        self.openapi_schema: dict[str, Any] | None = None
        self.openapi_specs = kwargs.pop('openapi_specs') if 'openapi_specs' in kwargs else OpenAPISpec()
        super().__init__(*args, **kwargs)
        self.routes = []
        self.apply_lock = False
        self.__all_classes = None
        self.configure()
        self.register_listener(parent)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if await self.handle_request(scope, receive, send) != Handled.NONE:
            return
        await self.not_found(scope, receive, send)

    async def handle_request(self, scope: Scope, receive: Receive, send: Send) -> Handled:
        assert scope["type"] in ("http", "websocket")
        scope_http = scope["type"] == "http"
        if "router" not in scope:
            scope["router"] = self

        partial = None
        for route in self.routes:
            match, child_scope = route.matches(scope)
            if match == Match.FULL:
                scope.update(child_scope)
                await route.handle(scope, receive, send)
                return Handled.FULL
            elif match == Match.PARTIAL and partial is None:
                partial = route
                partial_scope = child_scope
                break

        if partial is not None:
            scope.update(partial_scope)
            await partial.handle(scope, receive, send)
            return Handled.PARTIAL

        route_path = get_route_path(scope)
        if scope_http and route_path != "/":
            redirect_scope = dict(scope)
            if route_path.endswith("/"):
                redirect_scope["path"] = redirect_scope["path"].rstrip("/")
            else:
                redirect_scope["path"] = redirect_scope["path"] + "/"

            for route in self.routes:
                match, child_scope = route.matches(redirect_scope)
                if match != Match.NONE:
                    redirect_url = URL(scope=redirect_scope)
                    response = RedirectResponse(url=str(redirect_url))
                    await response(scope, receive, send)
                    return Handled.FULL

        if not scope_http:
            return Handled.NONE

        klass: type[ControllerABC] = None
        if self.all_classes:
            route_path = get_route_path(scope)
            posix = "".join(PurePosixPath(route_path).parts[:2])
            klass = self.all_classes.get(posix, None)
            if not klass:
                return Handled.NONE

            descriptor = klass.descriptor
            match, child_scope = descriptor.matches(scope)
            if match == Match.NONE:
                return Handled.NONE

            scope.update(child_scope)

        if klass and descriptor.handle_request:
            partial = None
            config = self.get_configuration()
            instance: ControllerABC = klass(config=config)
            if not instance.has_published_methods:
                return Handled.NONE
            for func in instance.published_methods:
                match, child_scope = func.published.matches(scope)
                if match == Match.FULL:
                    endpoint = getattr(instance, func.__name__)
                    child_scope.update({'endpoint': endpoint})
                    scope.update(child_scope)
                    await func.published.handle(scope, receive, send)
                    return Handled.FULL
                elif match == Match.PARTIAL and partial is None:
                    partial = func
                    partial_scope = child_scope

            if partial is not None:
                endpoint = getattr(instance, partial.__name__)
                partial_scope.update({'endpoint': endpoint})
                scope.update(partial_scope)
                await partial.published.handle(scope, receive, send)
                return Handled.FULL

            return Handled.NONE

        partial = None
        for func in self.published_methods:
            match, child_scope = func.published.matches(scope)
            if match == Match.FULL:
                endpoint = getattr(self, func.__name__)
                child_scope.update({'endpoint': endpoint})
                scope.update(child_scope)
                await func.published.handle(scope, receive, send)
                return Handled.FULL
            elif match == Match.PARTIAL and partial is None:
                partial = func
                partial_scope = child_scope

        if partial is not None:
            endpoint = getattr(self, partial.__name__)
            partial_scope.update({'endpoint': endpoint})
            scope.update(partial_scope)
            await partial.published.handle(scope, receive, send)
            return Handled.FULL

        return Handled.NONE

    def module_matches(self, scope: Scope) -> tuple[Match, Scope]:
        child_scope = {}

        if not self.all_classes:
            return Match.FULL, child_scope

        output = Match.NONE
        if scope["type"] == "http":
            root_path = scope.get("root_path", "")
            route_path = get_route_path(scope)
            posix = "".join(PurePosixPath(route_path).parts[:2])
            if posix in self.all_classes:
                klass = self.all_classes[posix]
                descriptor = klass.descriptor
                match = descriptor.path_regex.match(route_path)
                if match:
                    matched_params = match.groupdict()
                    for key, value in matched_params.items():
                        matched_params[key] = descriptor.param_convertors[key].convert(value)
                    remaining_path = "/" + matched_params.pop("path")
                    matched_path = route_path[: -len(remaining_path)]
                    path_params = dict(scope.get("path_params", {}))
                    path_params.update(matched_params)
                    child_scope = {
                        "path_params": path_params,
                        "app_root_path": scope.get("app_root_path", root_path),
                        "root_path": root_path + matched_path,
                        "class": klass,
                    }
                    output = Match.FULL

        return output, child_scope

    def do_configure(self):
        async def openapi(req: Request) -> JSONResponse:
            root_path = req.scope.get("root_path", "").rstrip("/")
            schema = self.openapi()
            if root_path:
                server_urls = {s.get("url") for s in schema.get("servers", [])}
                if root_path not in server_urls:
                    schema = dict(schema)
                    schema["servers"] = [{"url": root_path}] + schema.get(
                        "servers", []
                    )
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
        self.mount(self.openapi_specs.docs_url + '/static',
                   StaticFiles(packages=[('artanis.asgi.openapi', 'static'), ]), name='static')

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

    @staticmethod
    async def not_found(scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "websocket":
            websocket_close = WebSocketClose()
            await websocket_close(scope, receive, send)
            return

        if "app" in scope:
            raise HTTPException(status_code=404)
        else:
            response = PlainTextResponse("Not Found", status_code=404)
        await response(scope, receive, send)

    @property
    def all_classes(self):
        return self.__all_classes

    def register_listener(self, parent: StartableService):

        def on_started(sender: StartableService):
            self.load_classes()

        if self.base_modules:
            parent.add_listener(StartableListener(started_func=on_started))

    def load_classes(self):
        if (not self.base_modules) or self.__all_classes:
            return
        __all = import_function(f"{self.base_modules}:__all__")
        self.__all_classes = dict([self.__get_package_class(klass_name, self.base_modules) \
                                   for klass_name in __all])

    def __get_package_class(self, class_name: str, base_path: str | None = None, module_name: str | None = None):
        package = f"{self.base_modules if not base_path else base_path}.{class_name if not module_name else module_name}:{class_name}"
        return f"/{class_name}", import_function(package)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Router) and self.routes == other.routes

    def add_route(
            self,
            path: str,
            endpoint: Callable[[Request], Awaitable[Response] | Response],
            methods: Collection[str] | None = None,
            name: str | None = None,
            include_in_schema: bool = True,
    ) -> None:
        route = Route(path, endpoint=endpoint, methods=methods, name=name, include_in_schema=include_in_schema)
        self.routes.append(route)

    def mount(
            self,
            path: str,
            app: ASGIApp,
            name: str | None = None
    ) -> None:
        route = Mount(path, app=app, name=name)
        self.routes.append(route)
