#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2025 Busana Apparel Group. All rights reserved.
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

from typing import Callable, Optional

from artanis.config import Configuration
from artanis.utils import load_ecf_modules
from . import url

default_field_init: Optional[Callable[..., None]] = None


def patched_field_init(self, *args, null=True, **kwargs
                       ) -> None:
    label = kwargs.pop("label", None)
    if label:
        kwargs["description"] = label
    default_field_init(self, *args, null=null, **kwargs)


async def configure_database(config: Configuration):
    global default_field_init
    db_url: str = config.get_property_value(config.ARTANIS_DB_CONNECTION, '')
    u = url.make_url(db_url)
    db_credentials = dict(
        host=u.host,
        database=u.database,
        port=u.port if u.port else 5432,
        user=u.username,
        password=u.password
    )
    db_default = dict(
        engine="artanis.sqlentity",
        credentials=db_credentials
    )
    db_connection = dict(
        default=db_default
    )

    models = dict(
        models=["ecf.tbl"],
        default_connection="default"
    )
    db_models = dict(
        models=models
    )
    db_config = dict(connections=db_connection, apps=db_models)
    from tortoise.fields.base import Field
    default_field_init = Field.__init__
    Field.__init__ = patched_field_init
    from tortoise import Tortoise
    load_ecf_modules("ecf.tbl", True)
    await Tortoise.init(config=db_config, _enable_global_fallback=True)


async def setup_all(config: Configuration) -> None:
    from tortoise import Tortoise
    await Tortoise.generate_schemas()


async def unconfigure_database(config: Configuration):
    from tortoise import Tortoise
    await Tortoise.close_connections()
