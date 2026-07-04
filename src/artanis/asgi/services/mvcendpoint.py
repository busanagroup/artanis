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
import typing as t

import pydantic
from starlette.requests import Request

from artanis import concurrency
from artanis.asgi import schemas
from artanis.asgi import types, http
from artanis.asgi.asgiendpoint import Descriptor, ASGIEndPoint, published
from artanis.asgi.auth.validator import MVCAccessValidator
from artanis.asgi.routing.routes.http import BaseHTTPEndpointWrapper, SafeExecution
from artanis.asgi.schemas.response import DefaultResponse, DefaultResp


class DataListReq(pydantic.BaseModel):
    params: t.Dict[str, t.Any] | None
    fields: t.List[str] | None
    data: t.Any | None
    limit: int
    offset: int

class DataListResp(DefaultResp):
    params: t.Dict[str, t.Any] | None
    offset: int
    total: int

class CRUDReq(pydantic.BaseModel):
    params: t.Dict[str, t.Any] | None
    fields: t.List[str] | None
    data: t.Any | None

class EditResp(DefaultResp):
    params: t.Dict[str, t.Any] | None

DataListRequest = t.Annotated[schemas.Schema, schemas.SchemaMetadata(DataListReq)]
DataListResponse = t.Annotated[schemas.Schema, schemas.SchemaMetadata(DataListResp)]
CRUDRequest = t.Annotated[schemas.Schema, schemas.SchemaMetadata(CRUDReq)]
EditRequest = t.Annotated[schemas.Schema, schemas.SchemaMetadata(EditResp)]


class MVCEndpointWrapper(BaseHTTPEndpointWrapper):

    async def __call__(self, scope: types.Scope, receive: types.Receive, send: types.Send) -> None:
        request = http.Request(scope, receive=receive)
        injected_func = functools.partial(self.handler, request)
        if concurrency.is_async(self.handler):
            injected_func = functools.partial(SafeExecution.safe_execute, injected_func)
        response = await concurrency.run(injected_func)
        response = self._build_api_response(response)
        await response(scope, receive, send)


class MVCEndpointDescriptor(Descriptor):
    handle_request = True


class MVCEndPoint(ASGIEndPoint):
    descriptor: Descriptor = MVCEndpointDescriptor()
    base_path = "/mvc"
    base_modules = "ecf.mvc"
    openapi_support = True
    access_validator = MVCAccessValidator()

    @published(path="/definition", endpoint_wrapper=MVCEndpointWrapper)
    async def definitions(self, request: Request) -> DefaultResponse:
        """
        parameters:
        - in: path
          name: service_name
          schema:
            type: string
          required: true
          description: Get service definition
        """
        scope = request.scope
        instance = scope.get("module_instance")
        descriptor = instance.descriptor
        data = dict(
            jsonFields=dict(attrs={}),
            service=descriptor.name,
            fields=[field.field_info() for field in descriptor.get_fields()],
        )
        return DefaultResponse(status=0, data=data)

    @published(path="/open")
    async def get_data(self, data: DataListRequest, request: Request) -> DataListResponse:
        scope = request.scope
        instance = scope.get("module_instance")
        descriptor = instance.descriptor
        return DataListResponse(status=0, offset=0, total=40, data={'hello': "world"})

    @published(path="/pgmredir")
    async def pgmredir(self, request: Request):
        return {'hello': "world"}

    @published(path="/verify")
    async def verify(self, request: Request):
        return {'hello': "world"}

    @published(path="/initialize")
    async def initialize(self, request: Request):
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
