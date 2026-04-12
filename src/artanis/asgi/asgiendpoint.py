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

import enum
import inspect
import typing as t
from pathlib import PurePosixPath

from fastapi import APIRouter, params
from fastapi._compat import (
    ModelField,
    lenient_issubclass,
)
from fastapi.datastructures import Default, DefaultPlaceholder
from fastapi.dependencies.utils import get_typed_return_annotation, get_stream_item_type, get_dependant, \
    get_flat_dependant, _should_embed_body_fields, get_body_field, get_parameterless_sub_dependant
from fastapi.routing import request_response, get_request_handler
from fastapi.sse import EventSourceResponse, ServerSentEvent
from fastapi.types import IncEx
from fastapi.utils import generate_unique_id, is_body_allowed_for_status_code, create_model_field
from starlette.datastructures import URL
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse, PlainTextResponse, JSONResponse, Response, HTMLResponse
from starlette.routing import Match, compile_path, Route
from starlette.types import Scope, Send, Receive
from starlette.websockets import WebSocketClose

from artanis.abc.configurable import Configurable
from artanis.abc.service import StartableService
from artanis.abc.startable import StartableListener
from artanis.asgi.asgiservice import ASGIService, OpenAPISpec
from artanis.asgi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from artanis.asgi.openapi.utils import get_openapi
from artanis.utils import get_route_path, get_name, import_function


class Handled(enum.Enum):
    NONE = 0
    PARTIAL = 1
    FULL = 2


class Descriptor:
    name: str
    path: str
    handle_request: bool = False
    openapi_support: bool = True
    default_tags: dict[str, t.Any] = {"permissions": ["access:secure"]}

    def __init__(self):
        self.path_format = None
        self.path_regex = None
        self.param_convertors = None

    def describe(self, name: str):
        self.name = name
        self.path = f"/{self.name}"
        self.path_regex, self.path_format, self.param_convertors = compile_path(self.path + "/{path:path}")

    def matches(self, scope: Scope) -> tuple[Match, Scope]:
        path_params: dict[str, t.Any]
        if scope["type"] in ("http", "websocket"):  # pragma: no branch
            root_path = scope.get("root_path", "")
            route_path = get_route_path(scope)
            match = self.path_regex.match(route_path)
            if match:
                matched_params = match.groupdict()
                for key, value in matched_params.items():
                    matched_params[key] = self.param_convertors[key].convert(value)
                remaining_path = "/" + matched_params.pop("path")
                matched_path = route_path[: -len(remaining_path)]
                path_params = scope.get("path_params", {})
                path_params.update(matched_params)
                child_scope = {
                    "path_params": path_params,
                    "app_root_path": scope.get("app_root_path", root_path),
                    "root_path": root_path + matched_path,
                }
                return Match.FULL, child_scope
        return Match.NONE, {}


def has_published_method(cls):
    for func_name, func in cls.__dict__.items():
        if hasattr(func, "published"):
            return True
    return False


class ControllerABC(Configurable):
    descriptor: Descriptor = None
    has_published_methods: bool = False

    def __init__(
            self,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if self.has_published_methods:
            descriptor: Published
            for descriptor in self.published_methods:
                func = getattr(self, descriptor.name)
                descriptor.prepare_endpoint(func)
                descriptor.methods = {"GET"} if descriptor.methods is None else set(descriptor.methods)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.has_published_methods = has_published_method(cls)
        if hasattr(cls, "descriptor"):
            klass = Descriptor if cls.descriptor is None else \
                cls.descriptor if inspect.isclass(cls.descriptor) else \
                    cls.descriptor.__class__
            cls.descriptor = klass()
            cls.descriptor.describe(cls.__name__)

        if cls.has_published_methods:
            cls.published_methods = []
            for _, func in cls.__dict__.items():
                if hasattr(func, "published"):
                    descriptor = func.published
                    tags: dict[str, t.Any] = cls.descriptor.default_tags
                    tags.update(descriptor.tags)
                    descriptor.tags = tags
                    # descriptor.prepare_endpoint(func)
                    cls.published_methods.append(descriptor)
                    del func.published


class Published:
    __safe_exec: t.Callable | None = None

    def __init__(
            self,
            name: str,
            path: str | None = None,
            methods: set[str] | t.Sequence[str] | None = None,
            include_in_schema: bool = True,
            response_model: t.Any = Default(None),
            response_class: type[Response] | DefaultPlaceholder = Default(JSONResponse),
            tags: dict[str, t.Any] | None = None,
            dependencies: t.Sequence[params.Depends] | None = None,
            description: str | None = None,
            generate_unique_id_function: t.Callable[[t.Any], str] | DefaultPlaceholder = Default(generate_unique_id),
            operation_id: str | None = None,
            status_code: int | None = None,
            response_model_include: IncEx | None = None,
            response_model_exclude: IncEx | None = None,
            response_model_by_alias: bool = True,
            response_model_exclude_unset: bool = False,
            response_model_exclude_defaults: bool = False,
            response_model_exclude_none: bool = False,
    ):
        self.name = name
        self.path = path if path else f"/{name}"
        self.methods = {"GET"} if methods is None else set(methods)
        self.include_in_schema = include_in_schema
        self.tags = {} if tags is None else tags
        self.dependencies = list(dependencies or [])
        self.stream_item_type: t.Any | None = None
        self.response_model = response_model
        self.response_class = response_class
        self.endpoint = None
        self.app = None
        self.dependant = None
        if "GET" in self.methods:
            self.methods.add("HEAD")
        self.path_regex, self.path_format, self.param_convertors = compile_path(self.path)
        self.description = description
        self.generate_unique_id_function = generate_unique_id_function
        self.operation_id = operation_id
        if isinstance(status_code, enum.IntEnum):
            status_code = int(status_code)
        self.status_code = status_code
        self.unique_id = None
        self._flat_dependant = None
        self._embed_body_fields = None
        self.body_field = None
        self.stream_item_field: ModelField | None = None
        self.stream_item_type = None
        self.response_field = None
        self.responses = {}
        self.response_fields = {}
        self.is_sse_stream = None
        self.is_json_stream = None
        self.response_model_include = response_model_include
        self.response_model_exclude = response_model_exclude
        self.response_model_by_alias = response_model_by_alias
        self.response_model_exclude_unset = response_model_exclude_unset
        self.response_model_exclude_defaults = response_model_exclude_defaults
        self.response_model_exclude_none = response_model_exclude_none

    def get_route_handler(self) -> t.Callable[[Request], t.Coroutine[t.Any, t.Any, Response]]:
        return get_request_handler(
            dependant=self.dependant,
            body_field=self.body_field,
            status_code=self.status_code,
            response_class=self.response_class,
            response_field=self.response_field,
            response_model_include=self.response_model_include,
            response_model_exclude=self.response_model_exclude,
            response_model_by_alias=self.response_model_by_alias,
            response_model_exclude_unset=self.response_model_exclude_unset,
            response_model_exclude_defaults=self.response_model_exclude_defaults,
            response_model_exclude_none=self.response_model_exclude_none,
            embed_body_fields=self._embed_body_fields,
            strict_content_type=True,
            stream_item_field=self.stream_item_field,
            is_json_stream=self.is_json_stream,
        )

    def prepare_endpoint(self, endpoint: t.Callable):
        assert callable(endpoint), "An endpoint must be a callable"
        self.endpoint = endpoint

        if isinstance(self.response_model, DefaultPlaceholder):
            return_annotation = get_typed_return_annotation(endpoint)
            if lenient_issubclass(return_annotation, Response):
                self.response_model = None
            else:
                stream_item = get_stream_item_type(return_annotation)
                if stream_item is not None:
                    if (
                            isinstance(self.response_class, DefaultPlaceholder)
                            or lenient_issubclass(self.response_class, EventSourceResponse)
                    ) and not lenient_issubclass(stream_item, ServerSentEvent):
                        self.stream_item_type = stream_item
                    self.response_model = None
                else:
                    self.response_model = return_annotation

        self.dependant = get_dependant(
            path=self.path_format,
            call=self.endpoint,
            scope="function"
        )
        if isinstance(self.generate_unique_id_function, DefaultPlaceholder):
            current_generate_unique_id: t.Callable[[t.Any], str] = (
                self.generate_unique_id_function.value
            )
        else:
            current_generate_unique_id = self.generate_unique_id_function
        self.unique_id = self.operation_id or current_generate_unique_id(self)
        # normalize enums e.g. http.HTTPStatus
        if self.response_model:
            assert is_body_allowed_for_status_code(self.status_code), (
                f"Status code {self.status_code} must not have a response body"
            )
            response_name = "Response_" + self.unique_id
            self.response_field = create_model_field(
                name=response_name,
                type_=self.response_model,
                mode="serialization",
            )
        else:
            self.response_field = None  # type: ignore
        if self.stream_item_type:
            stream_item_name = "StreamItem_" + self.unique_id
            self.stream_item_field: ModelField | None = create_model_field(
                name=stream_item_name,
                type_=self.stream_item_type,
                mode="serialization",
            )
        else:
            self.stream_item_field = None

        self.description = self.description or inspect.cleandoc(self.endpoint.__doc__ or "")
        self.description = self.description.split("\f")[0].strip()
        response_fields = {}
        for additional_status_code, response in self.responses.items():
            assert isinstance(response, dict), "An additional response must be a dict"
            model = response.get("model")
            if model:
                assert is_body_allowed_for_status_code(additional_status_code), (
                    f"Status code {additional_status_code} must not have a response body"
                )
                response_name = f"Response_{additional_status_code}_{self.unique_id}"
                response_field = create_model_field(
                    name=response_name, type_=model, mode="serialization"
                )
                response_fields[additional_status_code] = response_field
        if response_fields:
            self.response_fields: dict[int | str, ModelField] = response_fields

        for depends in self.dependencies[::-1]:
            self.dependant.dependencies.insert(
                0,
                get_parameterless_sub_dependant(depends=depends, path=self.path_format),
            )
        self._flat_dependant = get_flat_dependant(self.dependant)
        self._embed_body_fields = _should_embed_body_fields(self._flat_dependant.body_params)
        self.body_field = get_body_field(
            flat_dependant=self._flat_dependant,
            name=self.unique_id,
            embed_body_fields=self._embed_body_fields,
        )
        # Detect generator endpoints that should stream as JSONL or SSE
        is_generator = (self.dependant.is_async_gen_callable or self.dependant.is_gen_callable)
        self.is_sse_stream = is_generator and lenient_issubclass(self.response_class, EventSourceResponse)
        self.is_json_stream = is_generator and isinstance(self.response_class, DefaultPlaceholder)
        self.app = request_response(safe_execute(self.get_route_handler()))

    def matches(self, scope: Scope) -> tuple[Match, Scope]:
        path_params: dict[str, t.Any]
        if scope["type"] == "http":
            route_path = get_route_path(scope)
            match = self.path_regex.match(route_path)
            if match:
                matched_params = match.groupdict()
                for key, value in matched_params.items():
                    matched_params[key] = self.param_convertors[key].convert(value)
                path_params = scope.get("path_params", {})
                path_params.update(matched_params)
                child_scope = {"path_params": path_params}
                if self.methods and scope["method"] not in self.methods:
                    return Match.PARTIAL, child_scope
                else:
                    return Match.FULL, child_scope
        return Match.NONE, {}

    async def handle(self, scope: Scope, receive: Receive, send: Send) -> None:
        if self.methods and scope["method"] not in self.methods:
            headers = {"Allow": ", ".join(self.methods)}
            if "app" in scope:
                raise HTTPException(status_code=405, headers=headers)
            else:
                response = PlainTextResponse("Method Not Allowed", status_code=405, headers=headers)
            await response(scope, receive, send)
        else:
            await self.app(scope, receive, send)

    @classmethod
    async def safe_execute(cls, func, *args, **kwargs):
        if not cls.__safe_exec:
            cls.__safe_exec = import_function("artanis.sqlentity.entity:safe_execute")
        return await cls.__safe_exec(func, *args, **kwargs)


def published(
        func: t.Callable[..., t.Any] | None = None,
        path: str | None = None,
        name: str | None = None,
        methods: list[str] | None = None,
        include_in_schema: bool = True,
        tags: dict[str, t.Any] | None = None,
        response_model: t.Any = Default(None),
        response_class: type[Response] | DefaultPlaceholder = Default(JSONResponse),
) -> t.Callable[..., t.Any]:
    if func:
        _name = get_name(func)
        func.published = Published(
            _name if name is None else name,
            path=path,
            methods=methods,
            include_in_schema=include_in_schema,
            tags=tags,
            response_class=response_class,
            response_model=response_model,
        )
        return func
    else:
        def wrapper(fnc):
            _name = get_name(fnc)
            fnc.published = Published(
                _name if name is None else name,
                path=path,
                methods=methods,
                include_in_schema=include_in_schema,
                tags=tags,
                response_class=response_class,
                response_model=response_model,
            )
            return fnc

        return wrapper


def safe_execute(
        func: t.Callable[[Request], t.Awaitable[Response] | Response]
) -> t.Callable[[Request], t.Coroutine[t.Any, t.Any, Response]]:
    async def app(
            request: Request
    ) -> Response:
        return await Published.safe_execute(func, request)

    return app


class EndPointRepository(dict[str, type[ControllerABC] | None]):

    def __init__(self, *args, base_modules: str | None = None, package_func: t.Callable | None = None, **kwargs):
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
        parent: ASGIService | None = kwargs.pop('parent') if 'parent' in kwargs else None
        super().__init__(*args, **kwargs)
        self.dynamic_load: bool = True
        self.parent = parent
        self.parent = parent
        self.webhooks = APIRouter()
        self.apply_lock = False
        self.__class_dir = None
        self.__all_classes = None
        self.routes = []
        self.openapi_schema: dict[str, t.Any] | None = None
        self.configure()
        self.register_listener(parent)

    async def handle_request(self, scope: Scope, receive: Receive, send: Send) -> Handled:
        assert scope["type"] in ("http", "websocket")
        scope_http = scope["type"] == "http"
        if "router" not in scope:
            scope["router"] = self

        partial: Route | None = None
        partial_scope = {}
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

        klass: type[ControllerABC] | None = None
        descriptor: Descriptor | None = None
        if self.all_classes:
            route_path = get_route_path(scope)
            posix_path = "".join(PurePosixPath(route_path).parts[:2])
            klass = self.all_classes.get(posix_path, None)
            if not klass:
                return Handled.NONE

            descriptor = klass.descriptor
            match, child_scope = descriptor.matches(scope)
            if match == Match.NONE:
                return Handled.NONE

            scope.update(child_scope)

        if klass and descriptor and descriptor.handle_request:
            partial = None
            config = self.get_configuration()

            instance: ControllerABC = klass(config=config)
            if not instance.has_published_methods:
                return Handled.NONE
            for endpoint in instance.published_methods:
                match, child_scope = endpoint.matches(scope)
                if match == Match.FULL:
                    child_scope.update({'endpoint': endpoint})
                    scope.update(child_scope)
                    await endpoint.handle(scope, receive, send)
                    return Handled.FULL
                elif match == Match.PARTIAL and partial is None:
                    child_scope.update({'endpoint': endpoint})
                    partial = endpoint
                    partial_scope = child_scope

            if partial is not None:
                scope.update(partial_scope)
                await partial.handle(scope, receive, send)
                return Handled.FULL

            return Handled.NONE

        partial = None
        if klass:
            scope.update({'module_class': klass})
        for endpoint in self.published_methods:
            match, child_scope = endpoint.matches(scope)
            if match == Match.FULL:
                scope.update(child_scope)
                await endpoint.handle(scope, receive, send)
                return Handled.FULL
            elif match == Match.PARTIAL and partial is None:
                partial = endpoint
                partial_scope = child_scope

        if partial is not None:
            scope.update(partial_scope)
            await partial.handle(scope, receive, send)
            return Handled.FULL

        return Handled.NONE

    def add_route(
            self,
            path: str,
            endpoint: t.Callable[[Request], t.Awaitable[Response] | Response],
            methods: list[str] | None = None,
            name: str | None = None,
            include_in_schema: bool = True,
    ) -> None:  # pragma: no cover
        route = Route(
            path,
            endpoint=endpoint,
            methods=methods,
            name=name,
            include_in_schema=include_in_schema,
        )
        self.routes.append(route)

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

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if await self.handle_request(scope, receive, send) != Handled.NONE:
            return
        await self.not_found(scope, receive, send)

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

    def register_listener(self, parent: StartableService | None):
        def on_started(sender: StartableService):
            self._load_class_dir()
            self._load_classes()

        if self.base_modules and parent:
            parent.add_listener(StartableListener(started_func=on_started))

    def do_configure(self):
        openapi_specs = self.parent.openapi_specs if self.parent else OpenAPISpec()
        if openapi_specs.openapi_url:
            async def openapi(req: Request) -> JSONResponse:
                root_path = req.scope.get("root_path", "").rstrip("/")
                schema: dict[str, t.Any] | None = self.openapi()
                if root_path and schema:
                    server_urls = {s.get("url") for s in schema.get("servers", [])}
                    if root_path not in server_urls:
                        schema = dict(schema)
                        schema["servers"] = ([{"url": root_path}] +
                                             schema.get("servers", [])
                                             )
                return JSONResponse(schema)

            self.add_route(openapi_specs.openapi_url, openapi, include_in_schema=False)

        if openapi_specs.openapi_url and openapi_specs.docs_url:

            async def swagger_ui_html(req: Request) -> HTMLResponse:
                root_path = req.scope.get("root_path", "").rstrip("/")
                openapi_url = root_path + openapi_specs.openapi_url
                oauth2_redirect_url = openapi_specs.swagger_ui_oauth2_redirect_url
                if oauth2_redirect_url:
                    oauth2_redirect_url = root_path + oauth2_redirect_url
                return get_swagger_ui_html(
                    openapi_url=openapi_url,
                    title=f"{openapi_specs.title} - Swagger UI",
                    oauth2_redirect_url=oauth2_redirect_url,
                    init_oauth=openapi_specs.swagger_ui_init_oauth,
                    swagger_ui_parameters=openapi_specs.swagger_ui_parameters,
                )

            self.add_route(openapi_specs.docs_url, swagger_ui_html, include_in_schema=False)

            if openapi_specs.swagger_ui_oauth2_redirect_url:
                async def swagger_ui_redirect(req: Request) -> HTMLResponse:
                    return get_swagger_ui_oauth2_redirect_html()

                self.add_route(
                    openapi_specs.swagger_ui_oauth2_redirect_url,
                    swagger_ui_redirect,
                    include_in_schema=False,
                )

    def openapi(self) -> dict[str, t.Any] | None:
        if not self.openapi_schema:
            openapi_specs = self.parent.openapi_specs if self.parent else OpenAPISpec()
            self.openapi_schema = get_openapi(
                title=openapi_specs.title,
                version=openapi_specs.version,
                openapi_version=openapi_specs.openapi_version,
                summary=openapi_specs.summary,
                description=openapi_specs.description,
                terms_of_service=openapi_specs.terms_of_service,
                contact=openapi_specs.contact,
                license_info=openapi_specs.license_info,
                routes=self.routes,
                webhooks=self.webhooks.routes,
                separate_input_output_schemas=openapi_specs.separate_input_output_schemas,
                external_docs=openapi_specs.external_docs,
            )
        return self.openapi_schema
