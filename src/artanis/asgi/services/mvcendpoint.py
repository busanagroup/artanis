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
import functools

from starlette.requests import Request

from artanis import concurrency
from artanis.asgi import types, http
from artanis.asgi.asgiendpoint import Descriptor, ASGIEndPoint, published
from artanis.asgi.auth.validator import MVCAccessValidator
from artanis.asgi.routing.routes.http import BaseHTTPEndpointWrapper, SafeExecution


class MVCEndpointWrapper(BaseHTTPEndpointWrapper):

    async def __call__(self, scope: types.Scope, receive: types.Receive, send: types.Send) -> None:
        request = http.Request(scope, receive=receive)
        injected_func = functools.partial(self.handler, request)
        if concurrency.is_async(self.handler):
            injected_func = functools.partial(SafeExecution.safe_execute, injected_func)
        response = await concurrency.run(injected_func)
        response = self._build_api_response(response)
        await response(scope, receive, send)


class MVCDescriptor(Descriptor):
    handle_request = True


class MVCEndPoint(ASGIEndPoint):
    descriptor: Descriptor = MVCDescriptor()
    base_path = "/mvc"
    base_modules = "ecf.mvc"
    openapi_support = True
    access_validator = MVCAccessValidator()

    @published(path="/pgmredir")
    async def pgmredir(self, request: Request):
        return {'hello': "world"}

    @published(path="/verify")
    async def verify(self, request: Request):
        return {'hello': "world"}

    @published(path="/definition", endpoint_wrapper=MVCEndpointWrapper)
    async def definitions(self, request: Request):
        return {'hello': "world"}

    @published(path="/initialize")
    async def initialize(self, request: Request):
        return {'hello': "world"}

    @published(path="/open")
    async def open(self, request: Request):
        return {'hello': "world"}

    @published(path="/get")
    async def get(self, request: Request):
        return {'hello': "world"}

    @published(path="/post")
    async def post(self, request: Request):
        return {'hello': "world"}

    @published(path="/initexec")
    async def initexec(self, request: Request):
        return {'hello': "world"}

    @published(path="/execute")
    async def execute(self, request: Request):
        return {'hello': "world"}

    @published(path="/print")
    async def print(self, request: Request):
        return {'hello': "world"}

    @published(path="/synchronize")
    async def sync(self, request: Request):
        return {'hello': "world"}

    @published(path="/initlookup")
    async def initlookup(self, request: Request):
        return {'hello': "world"}

    @published(path="/finalize")
    async def finalize(self, request: Request):
        return {'hello': "world"}
