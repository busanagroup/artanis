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
import importlib.util
import sys
import typing as t
from types import ModuleType

from artanis.exceptions import DependencyNotInstalled
from artanis.asgi.schemas.exceptions import SchemaParseError, SchemaValidationError
from artanis.asgi.types import Schema, SchemaList, SchemaMetadata

if t.TYPE_CHECKING:
    from artanis.asgi.schemas.adapter import Adapter
    from artanis.asgi.schemas.data_structures import Parameter

__all__ = [
    "Module",
    "SchemaValidationError",
    "SchemaParseError",
    "Schema",
    "SchemaList",
    "SchemaMetadata",
    "adapter",
    "fields",
    "lib",
    "schemas",
]

adapter: "Adapter"
fields: dict[t.Any, "Parameter"] = {}
lib: ModuleType | None = None
schemas: t.Any = None


class Module:
    SCHEMA_LIBS = ("pydantic", "typesystem", "marshmallow")

    def __init__(self) -> None:
        self.name: str
        self.lib: ModuleType

    @property
    def installed(self) -> list[str]:
        return [x for x in self.SCHEMA_LIBS if x in sys.modules or importlib.util.find_spec(x) is not None]

    @property
    def available(self) -> t.Generator[str, None, None]:
        for library in self.installed:
            try:
                importlib.import_module(f"artanis.asgi.schemas._libs.{library}")
                yield library
            except ModuleNotFoundError:
                pass

    def setup(self, library: str | None = None):
        try:
            if library is None:
                library = next(self.available)
        except StopIteration:
            raise DependencyNotInstalled(
                msg="No schema library is installed."
            )
        self.name = library
        self.lib = importlib.import_module(f"artanis.asgi.schemas._libs.{library}")

        global schemas, lib, fields, adapter, Field, Schema
        schemas = self.lib.schemas
        lib = self.lib.lib
        fields = self.lib.fields
        adapter = self.lib.adapter


# Find the first schema lib available and setup the module using it
_module = Module()
_module.setup()

# Check that at least one of the schema libs is installed
if _module.lib is None:
    raise DependencyNotInstalled(
        msg=f"Any of the schema libraries ({', '.join(_module.SCHEMA_LIBS)}) must be installed."
    )
