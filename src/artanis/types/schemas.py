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
import dataclasses
import typing as t

__all__ = ["Schema", "SchemaList", "SchemaMetadata", "get_schema_metadata", "is_schema", "is_schema_partial"]

Schema: t.TypeAlias = dict[str, t.Any]
SchemaList: t.TypeAlias = list[Schema]


@dataclasses.dataclass(frozen=True)
class SchemaMetadata:
    schema: t.Any
    partial: bool = False


def get_schema_metadata(obj: t.Any) -> SchemaMetadata:
    return getattr(obj, "__metadata__", [None])[0]


def is_schema(obj: t.Any) -> bool:
    return isinstance(get_schema_metadata(obj), SchemaMetadata)


def is_schema_partial(obj: t.Any) -> bool:
    return is_schema(obj) and get_schema_metadata(obj).partial
