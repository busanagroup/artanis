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
from typesystem import Definitions, Reference, Schema, fields

__all__ = [
    "APIError",
    "DropCollection",
    "LimitOffsetMeta",
    "LimitOffset",
    "PageNumberMeta",
    "PageNumber",
    "SCHEMAS",
]

SCHEMAS = Definitions()

APIError = Schema(
    title="APIError",
    fields={
        "status_code": fields.Integer(title="status_code", description="HTTP status code"),
        "detail": fields.Union(any_of=[fields.Object(), fields.String()], title="detail", description="Error detail"),
        "error": fields.String(title="type", description="Exception or error type", allow_null=True),
    },
)

DropCollection = Schema(
    title="DropCollection",
    fields={
        "deleted": fields.Integer(title="deleted", description="Number of deleted elements"),
    },
)

LimitOffsetMeta = Schema(
    title="LimitOffsetMeta",
    fields={
        "limit": fields.Integer(title="limit", description="Number of retrieved items"),
        "offset": fields.Integer(title="offset", description="Collection offset"),
        "count": fields.Integer(title="count", description="Total number of items", allow_null=True),
    },
)

LimitOffset = Schema(
    title="LimitOffset",
    fields={
        "meta": Reference(
            to="artanis.LimitOffsetMeta", definitions=SCHEMAS, title="meta", description="Pagination metadata"
        ),
        "data": fields.Array(title="data", description="Paginated data"),
    },
)

PageNumberMeta = Schema(
    title="PageNumberMeta",
    fields={
        "page": fields.Integer(title="page", description="Current page number"),
        "page_size": fields.Integer(title="page_size", description="Page size"),
        "count": fields.Integer(title="count", description="Total number of items", allow_null=True),
    },
)

PageNumber = Schema(
    title="PageNumber",
    fields={
        "meta": Reference(
            to="artanis.PageNumberMeta", definitions=SCHEMAS, title="meta", description="Pagination metadata"
        ),
        "data": fields.Array(title="data", description="Paginated data"),
    },
)

SCHEMAS = {
    "artanis.APIError": APIError,
    "artanis.DropCollection": DropCollection,
    "artanis.LimitOffsetMeta": LimitOffsetMeta,
    "artanis.LimitOffset": LimitOffset,
    "artanis.PageNumberMeta": PageNumberMeta,
    "artanis.PageNumber": PageNumber
}
