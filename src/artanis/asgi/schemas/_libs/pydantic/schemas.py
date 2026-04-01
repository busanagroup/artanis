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
import typing as t

from pydantic import BaseModel, Field

__all__ = [
    "APIError",
    "DropCollection",
    "LimitOffsetMeta",
    "LimitOffset",
    "PageNumberMeta",
    "PageNumber",
    "SCHEMAS",
]


class APIError(BaseModel):
    status_code: int = Field(title="status_code", description="HTTP status code")
    detail: str | dict[str, t.Any] = Field(title="detail", description="Error detail")
    error: str | None = Field(title="type", description="Exception or error type")


class DropCollection(BaseModel):
    deleted: int = Field(title="deleted", description="Number of deleted elements")


class LimitOffsetMeta(BaseModel):
    limit: int = Field(title="limit", description="Number of retrieved items")
    offset: int = Field(title="offset", description="Collection offset")
    count: int | None = Field(title="count", description="Total number of items")


class LimitOffset(BaseModel):
    meta: LimitOffsetMeta = Field(title="meta", description="Pagination metadata")
    data: list[t.Any] = Field(title="data", description="Paginated data")


class PageNumberMeta(BaseModel):
    page: int = Field(title="page", description="Current page number")
    page_size: int = Field(title="page_size", description="Page size")
    count: int | None = Field(title="count", description="Total number of items")


class PageNumber(BaseModel):
    meta: PageNumberMeta = Field(title="meta", description="Pagination metadata")
    data: list[t.Any] = Field(title="data", description="Paginated data")


SCHEMAS = {
    "artanis.APIError": APIError,
    "artanis.DropCollection": DropCollection,
    "artanis.LimitOffsetMeta": LimitOffsetMeta,
    "artanis.LimitOffset": LimitOffset,
    "artanis.PageNumberMeta": PageNumberMeta,
    "artanis.PageNumber": PageNumber
}
