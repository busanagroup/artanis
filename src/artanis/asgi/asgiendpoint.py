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

import inspect
import typing as t
from dataclasses import dataclass
from pathlib import PurePosixPath

from artanis import exceptions, concurrency
from artanis.abc.configurable import Configurable
from artanis.abc.service import StartableService
from artanis.abc.startable import StartableListener
from artanis.asgi import url, types
from artanis.asgi.routing import BaseRoute, Route
from artanis.asgi.routing.routes.http import HTTPFunctionWrapper
from artanis.asgi.schemas.routing import ParametersDescriptor
from artanis.utils import get_name, import_function, get_route_path


class Descriptor:
    name: str
    path: url.Path | str
    handle_request: bool = False

    def describe(self, name: str):
        self.name = name
        self.path = url.Path(f"/{self.name}")

    def match(self, scope: types.Scope) -> BaseRoute.Match:
        """Check if this route matches with given scope.

        :param scope: ASGI scope.
        :return: Match.
        """
        if scope["type"] not in ("http", "websocket"):
            return BaseRoute.Match.none
        m = self.path.match(scope["path"])
        return (
            BaseRoute.Match.full
            if m.match in (self.path.Match.exact, self.path.Match.partial)
            else BaseRoute.Match.none
        )


def has_published_method(cls):
    for func_name, func in cls.__dict__.items():
        if hasattr(func, "published"):
            return True
    return False


def prepare_endpoint(func: t.Callable[..., t.Any]):
    descriptor: Published = func.published
    descriptor.methods = {"GET"} if descriptor.methods is None else set(descriptor.methods)
    wrapped_endpoint = HTTPFunctionWrapper(func, signature=inspect.signature(func), pagination=descriptor.pagination)
    descriptor.endpoint = wrapped_endpoint
    descriptor.parameters._build(wrapped_endpoint)
    return func


class ControllerABC(Configurable):
    descriptor: Descriptor
    has_published_methods: bool = False

    def __init__(
            self,
            *args,
            func_name: str | None = None,
            **kwargs):
        super().__init__(*args, **kwargs)
        for descriptor in self.published_methods:
            if (func_name is None) or (func_name == descriptor.name):
                func = getattr(self, descriptor.name)
                descriptor.endpoint = func
                descriptor.methods = {"GET"} if descriptor.methods is None else set(descriptor.methods)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.has_published_methods = has_published_method(cls)
        if hasattr(cls, "descriptor"):
            cls.descriptor.describe(cls.__name__)
        cls.published_methods = []
        for _, func in cls.__dict__.items():
            if hasattr(func, "published"):
                descriptor = func.published
                cls.published_methods.append(descriptor)
                del func.published


@dataclass
class Published:
    path: str | url.Path | None = None
    name: str | None = None
    methods: list[str] | set[str] | None = None
    include_in_schema: bool = True
    pagination: types.Pagination | None = None
    tags: dict[str, t.Any] | None = None
    _endpoint: t.Callable[..., t.Any] | None = None
    _app: t.Callable[..., t.Any] | None = None

    def __post_init__(self):
        self.path = f"/{self.name}" if self.path is None else self.path
        self.path = url.Path(self.path)
        self.parameters = ParametersDescriptor(self)

    def match(self, scope: types.Scope) -> BaseRoute.Match:
        if scope["type"] != "http":
            return BaseRoute.Match.none

        m = BaseRoute.Match.full if self.path.match(scope["path"]).match == self.path.Match.exact \
            else BaseRoute.Match.none
        if m == BaseRoute.Match.none:
            return m
        return BaseRoute.Match.full if scope["method"] in self.methods else BaseRoute.Match.partial

    def endpoint_handlers(self) -> dict[str, t.Callable]:
        return {}

    def route_scope(self, scope: types.Scope) -> types.Scope:
        return types.Scope({})

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def app(self):
        return self._app

    @endpoint.setter
    def endpoint(self, value: t.Callable[..., t.Any] | None):
        if value:
            wrapped_endpoint = HTTPFunctionWrapper(value, signature=inspect.signature(value),
                                                   pagination=self.pagination)
            self.parameters._build(wrapped_endpoint)
        else:
            wrapped_endpoint = value
        self._app = wrapped_endpoint
        self._endpoint = wrapped_endpoint.handler

    async def __call__(self, scope: types.Scope, receive: types.Receive, send: types.Send) -> None:
        if scope["type"] == "http":
            await self.handle(types.Scope({**scope, **self.route_scope(scope)}), receive, send)

    async def handle(self, scope: types.Scope, receive: types.Receive, send: types.Send) -> None:
        await concurrency.run(self._app, scope, receive, send)


def published(
        func: t.Callable[..., t.Any] | None = None,
        path: str | url.Path | None = None,
        name: str | None = None,
        methods: list[str] | None = ["GET"],
        include_in_schema: bool = True,
        pagination: types.Pagination | None = None,
        tags: dict[str, t.Any] | None = {},
) -> t.Callable[..., t.Any]:
    if func:
        _name = get_name(func)
        func.published = Published(
            path=path,
            name=_name if name is None else name,
            methods=methods,
            include_in_schema=include_in_schema,
            pagination=pagination,
            tags=tags,
        )
        return func
    else:
        def wrapper(fnc):
            _name = get_name(fnc)
            fnc.published = Published(
                path=path,
                name=_name if name is None else name,
                methods=methods,
                include_in_schema=include_in_schema,
                pagination=pagination,
                tags=tags,
            )
            return fnc

        return wrapper


class ASGIEndPoint(ControllerABC):
    base_modules: str = None

    def __init__(self, *args, **kwargs):
        parent: StartableService = kwargs.pop('parent') if 'parent' in kwargs else None
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.__routes = None
        self.apply_lock = False
        self.__all_classes = None
        self.configure()
        self.register_listener(parent)

    def resolve_route(self, scope: types.Scope) -> tuple[BaseRoute, types.Scope]:

        klass: type[ControllerABC] | None = None
        if self.all_classes:
            route_path = get_route_path(scope)
            posix = "".join(PurePosixPath(route_path).parts[:2])
            klass = self.all_classes.get(posix, None)
            if not klass:
                raise exceptions.NotFoundException(
                    path=scope.get("root_path", "") + scope["path"], params=scope.get("path_params")
                )
            descriptor = klass.descriptor
            m = descriptor.path.match(scope["path"])
            match = BaseRoute.Match.full if m.match in (descriptor.path.Match.exact, descriptor.path.Match.partial) \
                else BaseRoute.Match.none
            if match == BaseRoute.Match.none:
                raise exceptions.NotFoundException(
                    path=scope.get("root_path", "") + scope["path"], params=scope.get("path_params")
                )
            scope.update({
                "root_path": str(url.Path(scope.get("root_path", "")) / (m.matched or "")),
                "path": str(url.Path("/") / (m.unmatched or "")),
            })
        descriptor = klass.descriptor if klass else None
        if klass and descriptor.handle_request:
            partial = None
            partial_allowed_methods: set[str] = set()
            config = self.get_configuration()
            instance: ControllerABC = klass(config=config)
            if not instance.has_published_methods:
                raise exceptions.NotFoundException(
                    path=scope.get("root_path", "") + scope["path"], params=scope.get("path_params")
                )
            for route in instance.published_methods:
                match = route.match(scope)
                if match == BaseRoute.Match.full:
                    route_scope = types.Scope({**scope, **route.route_scope(scope)})
                    return route, route_scope
                elif match == route.Match.partial:
                    partial = route
                    partial_allowed_methods |= route.methods

            if partial:
                route_scope = types.Scope({**scope, **partial.route_scope(scope)})
                raise exceptions.MethodNotAllowedException(
                    route_scope.get("root_path", "") + route_scope["path"], route_scope["method"],
                    partial_allowed_methods
                )

        partial = None
        partial_allowed_methods: set[str] = set()
        if not self.has_published_methods:
            raise exceptions.NotFoundException(
                path=scope.get("root_path", "") + scope["path"], params=scope.get("path_params")
            )
        for route in self.published_methods:
            match = route.match(scope)
            if match == BaseRoute.Match.full:
                route_scope = types.Scope({**scope, **route.route_scope(scope)})
                return route, route_scope
            elif match == route.Match.partial:
                partial = route
                partial_allowed_methods |= route.methods

        if partial:
            route_scope = types.Scope({**scope, **partial.route_scope(scope)})
            raise exceptions.MethodNotAllowedException(
                route_scope.get("root_path", "") + route_scope["path"], route_scope["method"], partial_allowed_methods
            )

        raise exceptions.NotFoundException(
            path=scope.get("root_path", "") + scope["path"], params=scope.get("path_params")
        )

    @property
    def routes(self):
        if not self.__routes:
            routes = []
            config = self.get_configuration()
            if self.all_classes:
                for klass in self.all_classes.values():
                    descriptor = klass.descriptor
                    if descriptor.handle_request:
                        if klass.has_published_methods:
                            instance: ControllerABC = klass(config=config)
                            for method in instance.published_methods:
                                path = f"{descriptor.path.path}{method.path.path}"
                                route = Route(
                                    path,
                                    method.endpoint,
                                    methods=method.methods,
                                    name=method.name,
                                    include_in_schema=method.include_in_schema,
                                    pagination=method.pagination,
                                    tags=method.tags
                                )
                                route._build(self.parent)
                                routes.append(route)
                    else:
                        for method in self.published_methods:
                            path = f"{descriptor.path.path}{method.path.path}"
                            route = Route(
                                path,
                                method.endpoint,
                                methods=method.methods,
                                name=method.name,
                                include_in_schema=method.include_in_schema,
                                pagination=method.pagination,
                                tags=method.tags
                            )
                            route._build(self.parent)
                            routes.append(route)
            else:
                for method in self.published_methods:
                    route = Route(
                        method.path.path,
                        method.endpoint,
                        methods=method.methods,
                        name=method.name,
                        include_in_schema=method.include_in_schema,
                        pagination=method.pagination,
                        tags=method.tags,
                    )
                    route._build(self.parent)
                    routes.append(route)
            self.__routes = routes
        return self.__routes

    def register_listener(self, parent: StartableService):
        def on_started(sender: StartableService):
            self.load_classes()

        if self.base_modules:
            parent.add_listener(StartableListener(started_func=on_started))

    @property
    def all_classes(self):
        return self.__all_classes

    def load_classes(self):
        if (not self.base_modules) or self.__all_classes:
            return
        __all = import_function(f"{self.base_modules}:__all__")
        self.__all_classes = dict([self.__get_package_class(klass_name, self.base_modules) \
                                   for klass_name in __all])

    def __get_package_class(self, class_name: str, base_path: str | None = None, module_name: str | None = None):
        package = f"{self.base_modules if not base_path else base_path}.{class_name if not module_name else module_name}:{class_name}"
        return f"/{class_name}", import_function(package)
