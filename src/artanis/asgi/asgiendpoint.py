#!/usr/bin/env python
# !/usr/bin/env python
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
from pathlib import PurePosixPath
from typing import Callable

from artanis import exceptions, concurrency
from artanis.abc.configurable import Configurable
from artanis.abc.service import StartableService
from artanis.abc.startable import StartableListener
from artanis.asgi import url, types, endpoints
from artanis.asgi.routing import BaseRoute, Route
from artanis.asgi.routing.routes.http import HTTPFunctionWrapper
from artanis.utils import get_name, import_function, get_route_path

__all__ = ["ASGIEndPoint", "published", "Descriptor", "ControllerABC"]


class Descriptor:
    name: str
    path: url.Path | str
    handle_request: bool = False
    default_tags: dict[str, t.Any] | None = {"permissions": ["access:secure"]}

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


class ControllerABC(Configurable):
    descriptor: Descriptor
    has_published_methods: bool = False

    def __init__(
            self,
            *args,
            func_path: str | None = None,
            **kwargs):
        super().__init__(*args, **kwargs)
        for descriptor in self.published_methods:
            if ((func_path is None) or
                    (descriptor.path.match(func_path).match in (
                            descriptor.path.Match.exact,
                            descriptor.path.Match.partial
                    ))
            ):
                func = getattr(self, descriptor.name)
                descriptor.app = func
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
                tags = dict(cls.descriptor.default_tags)
                tags.update(descriptor.tags)
                descriptor.tags = tags
                cls.published_methods.append(descriptor)
                del func.published


class Published(BaseRoute):

    def __init__(
            self,
            path: str | url.Path | None = None,
            name: str | None = None,
            methods: set[str] | t.Sequence[str] | None = None,
            include_in_schema: bool = True,
            pagination: types.Pagination | None = None,
            tags: dict[str, t.Any] | None = None,
    ):
        self._app: t.Callable[..., t.Any] | None = None
        self._endpoint: t.Callable[..., t.Any] | None = None
        self.pagination = pagination
        self.methods = {"GET"} if methods is None else set(methods)
        if "GET" in self.methods:
            self.methods.add("HEAD")
        super().__init__(
            f"/{name}" if path is None else path,
            None,
            name=name,
            include_in_schema=include_in_schema,
            tags=tags
        )

    def match(self, scope: types.Scope) -> BaseRoute.Match:
        if scope["type"] != "http":
            return BaseRoute.Match.none

        m = BaseRoute.Match.full if self.path.match(scope["path"]).match == self.path.Match.exact \
            else BaseRoute.Match.none
        if m == BaseRoute.Match.none:
            return m
        return BaseRoute.Match.full if scope["method"] in self.methods else BaseRoute.Match.partial

    def route_scope(self, scope: types.Scope) -> types.Scope:
        return types.Scope({})

    @property
    def app(self):
        return self._app

    @app.setter
    def app(self, value):
        wrapped_endpoint = None
        if value:
            wrapped_endpoint = HTTPFunctionWrapper(value, signature=inspect.signature(value),
                                                   pagination=self.pagination)
            self.endpoint = wrapped_endpoint.handler
        self._app = wrapped_endpoint

    @property
    def endpoint(self):
        return self._endpoint

    @endpoint.setter
    def endpoint(self, value: t.Callable[..., t.Any] | None):
        self._endpoint = value

    async def __call__(self, scope: types.Scope, receive: types.Receive, send: types.Send) -> None:
        if scope["type"] == "http":
            await self.handle(types.Scope({**scope, **self.route_scope(scope)}), receive, send)

    async def handle(self, scope: types.Scope, receive: types.Receive, send: types.Send) -> None:
        await concurrency.run(self.app, scope, receive, send)

    def __hash__(self) -> int:
        return hash((self.app, self.path, self.name, tuple(self.methods)))

    def __eq__(self, other: t.Any) -> bool:
        return (
                isinstance(other, Published)
                and self.path == other.path
                and self.app == other.app
                and self.name == other.name
                and self.methods == other.methods
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path!r}, name={self.name!r}, methods={sorted(self.methods)!r})"

    @staticmethod
    def is_endpoint(x: t.Callable | type[endpoints.HTTPEndpoint]) -> t.TypeGuard[type[endpoints.HTTPEndpoint]]:
        return inspect.isclass(x) and issubclass(x, endpoints.HTTPEndpoint)

    def endpoint_handlers(self) -> dict[str, t.Callable]:
        if self.is_endpoint(self.endpoint):
            return {
                method: handler
                for method, handler in self.endpoint.allowed_handlers().items()
                if method in self.methods
            }

        return {method: self.endpoint for method in self.methods}



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


class EndPointRepository(dict[str, type[ControllerABC] | None]):

    def __init__(self, *args, base_modules: str | None = None, package_func: Callable | None = None, **kwargs):
        self.base_modules = base_modules
        self.package_func = package_func
        super().__init__(*args, **kwargs)

    def __getitem__(self, item):
        value = super().__getitem__(item)
        return self.validate(item, value)

    def get(self, key: str, *args, **kwargs):
        value = super().get(key, *args, **kwargs)
        return self.validate(key, value)

    def values(self):
        return [self.get(item) for item in self.keys()]

    def validate(self, key, value):
        klass = value
        if isinstance(value, str):
            klass = self.package_func(value, self.base_modules)
            self.__setitem__(key, klass)
        return klass


class ASGIEndPoint(ControllerABC):
    base_modules: str = None

    def __init__(self, *args, **kwargs):
        parent: StartableService = kwargs.pop('parent') if 'parent' in kwargs else None
        super().__init__(*args, **kwargs)
        self.dynamic_load: bool = True
        self.parent = parent
        self.__routes = None
        self.apply_lock = False
        self.__class_dir = None
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
                "module_base": self.base_modules,
                "module_path": posix,
                "module_class": klass,
                "path": str(url.Path("/") / (m.unmatched or "")),
            })
        descriptor = klass.descriptor if klass else None
        if klass and descriptor.handle_request:
            partial = None
            partial_allowed_methods: set[str] = set()
            config = self.get_configuration()
            func_name = scope['path']
            instance: ControllerABC = klass(config=config, func_path=func_name)
            if not instance.has_published_methods:
                raise exceptions.NotFoundException(
                    path=scope.get("root_path", "") + scope["path"], params=scope.get("path_params")
                )
            for route in instance.published_methods:
                match = route.match(scope)
                if match == BaseRoute.Match.full:
                    route_scope = types.Scope({**scope, **route.route_scope(scope)})
                    route._build(self.parent)
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
                route._build(self.parent)
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
            self._load_class_dir()
            self._load_classes()

        if self.base_modules:
            parent.add_listener(StartableListener(started_func=on_started))

    @property
    def all_classes(self):
        return self.__all_classes

    def _load_class_dir(self):
        if (not self.base_modules) or self.__class_dir:
            return
        self.__class_dir = import_function(f"{self.base_modules}:__all__")

    def _load_classes(self):
        if (not self.base_modules) or self.__all_classes:
            return
        self.__all_classes = dict([(f"/{klass_name}", self.__get_package_class(klass_name, self.base_modules)) \
                                   for klass_name in self.__class_dir]) \
            if not self.dynamic_load else EndPointRepository(
            [(f"/{klass_name}", klass_name) for klass_name in self.__class_dir],
            base_modules=self.base_modules,
            package_func=self.__get_package_class)

    def __get_package_class(self, class_name: str, base_path: str | None = None, module_name: str | None = None):
        package = f"{self.base_modules if not base_path else base_path}.{class_name if not module_name else module_name}:{class_name}"
        return import_function(package)
