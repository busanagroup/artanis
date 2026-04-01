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

from typing import NotRequired

__all__ = [
    "OpenAPISpecInfoContact",
    "OpenAPISpecInfoLicense",
    "OpenAPISpecInfo",
    "OpenAPISpecServerVariable",
    "OpenAPISpecServer",
    "OpenAPISpecExternalDocs",
    "OpenAPISpecTag",
    "OpenAPISpecSecurity",
    "OpenAPISpec",
]


class OpenAPISpecInfoContact(t.TypedDict):
    name: str
    url: str
    email: str


class OpenAPISpecInfoLicense(t.TypedDict):
    name: str
    identifier: NotRequired[str | None]
    url: NotRequired[str | None]


class OpenAPISpecInfo(t.TypedDict):
    title: str
    summary: NotRequired[str | None]
    description: NotRequired[str | None]
    termsOfService: NotRequired[str | None]
    contact: NotRequired[OpenAPISpecInfoContact | None]
    license: NotRequired[OpenAPISpecInfoLicense | None]
    version: str


class OpenAPISpecServerVariable(t.TypedDict):
    default: str
    enum: NotRequired[list[str] | None]
    description: NotRequired[str | None]


class OpenAPISpecServer(t.TypedDict):
    url: str
    description: NotRequired[str | None]
    variables: NotRequired[dict[str, OpenAPISpecServerVariable] | None]


class OpenAPISpecExternalDocs(t.TypedDict):
    url: str
    description: NotRequired[str | None]


class OpenAPISpecTag(t.TypedDict):
    name: str
    description: NotRequired[str | None]
    externalDocs: NotRequired[OpenAPISpecExternalDocs | None]


OpenAPISpecSecurity = dict[str, list[str]]


class OpenAPISpec(t.TypedDict):
    info: OpenAPISpecInfo
    servers: NotRequired[list[OpenAPISpecServer] | None]
    security: NotRequired[list[OpenAPISpecSecurity] | None]
    tags: NotRequired[list[OpenAPISpecTag] | None]
    externalDocs: NotRequired[OpenAPISpecExternalDocs | None]
