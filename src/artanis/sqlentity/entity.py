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

import types
import typing as t

from artanis import concurrency
from artanis.config import Configuration
from artanis.sqlentity.sqlorm import Entity
from artanis.utils import import_ecf_module

__ecf_tbl: types.ModuleType | None = None
__config: Configuration = Configuration.get_default_instance(create_instance=False)


def get_table_repository() -> types.ModuleType:
    global __ecf_tbl
    if __ecf_tbl is None:
        __ecf_tbl = t.cast(types.ModuleType, import_ecf_module("ecf.tbl"))
    return __ecf_tbl


def get_entity(table_name: str) -> t.Type[Entity]:
    repo = get_table_repository()
    result: t.Type[Entity] = t.cast(t.Type[Entity], getattr(repo, table_name, None))
    if not result:
        raise Exception(f'model "{table_name}" has not been implemented')
    return result


def get_entity_list() -> list[str]:
    repository = get_table_repository()
    return t.cast(list[str], repository.__all__)


def get_entities() -> list[t.Type[Entity]]:
    repository = get_table_repository()
    return [t.cast(t.Type[Entity], getattr(repository, table, None)) for table in repository.__all__]


def get_entity_field_info(entity: t.Type[Entity], field_name: str):
    return getattr(entity, field_name, None)


async def safe_execute(func: t.Callable[concurrency.P, concurrency.R] |
                             t.Callable[concurrency.P, t.Awaitable[concurrency.R]],
                       *args, **kwargs) -> t.Any:
    return await concurrency.run(func, *args, **kwargs) # noqa


async def record_exist(table_name: t.Type[Entity] | str, *args, **kwargs) -> tuple[bool, t.Any]:
    klass: t.Type[Entity] = get_entity(table_name) if isinstance(table_name, str) else table_name
    return await klass.record_exist(*args, **kwargs)
