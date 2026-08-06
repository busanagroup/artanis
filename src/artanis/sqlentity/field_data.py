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

from typing import overload, Any, Literal
from uuid import uuid7

from tortoise.fields import UUIDField as Tortoise_UUIDField


class UUIDField(Tortoise_UUIDField):

    class _db_postgres:
        SQL_TYPE = "UUID"
        GENERATED_SQL = "UUID PRIMARY KEY DEFAULT uuidv7()"

    @overload
    def __init__(self: UUIDField, *, null: Literal[False] = False, **kwargs: Any) -> None: ...

    @overload
    def __init__(self: UUIDField, *, null: Literal[True], **kwargs: Any) -> None: ...

    def __init__(self, **kwargs: Any) -> None:
        if kwargs.get("primary_key") or kwargs.get("pk", False):
            kwargs["generated"] = bool(kwargs.get("generated", True))
            if "default" not in kwargs:
                kwargs["default"] = uuid7
        super().__init__(**kwargs)

