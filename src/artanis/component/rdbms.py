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

from asyncio import current_task

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_scoped_session,
    async_sessionmaker, AsyncEngine
)

from artanis.config import Configuration
from artanis.sqlentity.sqlapool import AsyncQueuePool


def create_db_engine(db_url, **kwargs) -> AsyncEngine:
    return create_async_engine(db_url, poolclass=AsyncQueuePool, **kwargs)

def create_db_session(engine: AsyncEngine):
    return async_sessionmaker(engine, autoflush=False, expire_on_commit=False, autocommit=False)

def create_scoped_session(db_session: async_sessionmaker):
    return async_scoped_session(db_session, scopefunc=current_task)

async def configure_database(config: Configuration):
    if not config or hasattr(config.container, 'db_engine'):
        return

    db_url: str = config.get_property_value(config.ARTANIS_DB_CONNECTION, '')
    db_schema: str = config.get_property_value(config.ARTANIS_DB_SCHEMA, '')
    pool_size: int = int(config.get_property_value(config.ARTANIS_DB_POOL_SIZE, 4))
    db_engine = create_db_engine(db_url, pool_size=pool_size)
    db_session = create_db_session(db_engine)
    scoped_session = create_scoped_session(db_session)
    config.container.db_engine = db_engine
    config.container.db_session = db_session
    config.container.scoped_session = scoped_session
    config.container.db_metadata = MetaData(schema=db_schema) if db_schema else MetaData()


async def setup_all(config: Configuration, create_tables: bool = False):
    if not create_tables:
        return
    db_engine = config.container.db_engine
    db_metadata = config.container.db_metadata
    async with db_engine.begin() as conn:
        await conn.run_sync(db_metadata.create_all)


async def unconfigure_database(config: Configuration):
    if not hasattr(config.container, 'db_engine'):
        return
    try:
        await config.container.db_engine.dispose()
    except:
        pass