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
from http.cookies import SimpleCookie
from urllib.parse import parse_qsl

from artanis.asgi import http, routing, types
from artanis.injection.components import Component, Components

__all__ = [
    "MethodComponent",
    "URLComponent",
    "SchemeComponent",
    "ServerComponent",
    "PathComponent",
    "PathParamsComponent",
    "QueryStringComponent",
    "QueryParamsComponent",
    "HeadersComponent",
    "BodyComponent",
    "ASGI_COMPONENTS",
]


class MethodComponent(Component):
    def resolve(self, scope: types.Scope) -> types.Method:
        return types.Method(scope["method"])


class URLComponent(Component):
    def resolve(self, scope: types.Scope) -> types.URL:
        host, port = scope.get("server", ["", None])
        scheme = scope.get("scheme", "")
        path = scope.get("path", "")
        query = scope.get("query_string", b"").decode()

        if (scheme == "http" and port in (80, None)) or (scheme == "https" and port in (443, None)):
            port = None

        if port:
            host += f":{port}"

        if query:
            path += f"?{query}"

        return types.URL(f"{scheme}://{host}{path}")


class SchemeComponent(Component):
    def resolve(self, scope: types.Scope) -> types.Scheme:
        return types.Scheme(scope["scheme"])


class ServerComponent(Component):
    def resolve(self, scope: types.Scope) -> types.Server:
        return types.Server(scope["server"][0], int(scope["server"][1]) if scope["server"][1] else None)


class PathComponent(Component):
    def resolve(self, scope: types.Scope) -> types.Path:
        return types.Path(scope.get("root_path", "")) / types.Path(scope["path"])


class PathParamsComponent(Component):
    def resolve(self, scope: types.Scope, route: routing.BaseRoute) -> types.PathParams:
        return types.PathParams(route.path.match(scope["path"]).parameters or {})


class QueryStringComponent(Component):
    def resolve(self, scope: types.Scope) -> types.QueryString:
        return types.QueryString(scope["query_string"].decode())


class QueryParamsComponent(Component):
    def resolve(self, query: types.QueryString) -> types.QueryParams:
        return types.QueryParams(parse_qsl(query))


class HeadersComponent(Component):
    def resolve(self, request: http.Request) -> types.Headers:
        return request.headers


class CookiesComponent(Component):
    def resolve(self, headers: types.Headers) -> types.Cookies:
        cookie = SimpleCookie()
        cookie.load(headers.get("cookie", ""))
        return types.Cookies(
            {
                str(name): {**{str(k): str(v) for k, v in morsel.items()}, "value": morsel.value}
                for name, morsel in cookie.items()
            }
        )


class BodyComponent(Component):
    async def resolve(self, receive: types.Receive) -> types.Body:
        body = b""
        while True:
            message = await receive()
            if not message["type"] == "http.request":  # pragma: no cover
                raise Exception(f"Unexpected ASGI message type '{message['type']}'.")
            body += message.get("body", b"")
            if not message.get("more_body", False):
                break

        return types.Body(body)


ASGI_COMPONENTS = Components(
    [
        MethodComponent(),
        URLComponent(),
        SchemeComponent(),
        ServerComponent(),
        PathComponent(),
        PathParamsComponent(),
        QueryStringComponent(),
        QueryParamsComponent(),
        HeadersComponent(),
        CookiesComponent(),
        BodyComponent(),
    ]
)
