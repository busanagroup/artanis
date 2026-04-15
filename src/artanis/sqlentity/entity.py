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

import inspect
import types

from artanis.config import Configuration
from artanis.sqlentity.sqlorm import Session, Entity
from artanis.utils import import_ecf_module

__config: Configuration = Configuration.get_default_instance(create_instance=False)
__ecf_tbl: types.ModuleType | None = None


def get_table_repository():
    global __ecf_tbl
    if not __ecf_tbl:
        __ecf_tbl = import_ecf_module("ecf.tbl")
    return __ecf_tbl


def get_entity(table_name: str):
    repo = get_table_repository()
    result = getattr(repo, table_name, None)
    if not result:
        raise Exception(f'model "{table_name}" has not been implemented')
    return result


def get_user_name(user_session):
    return user_session if isinstance(user_session, str) else \
        None if user_session is None else \
            user_session.user_name if hasattr(user_session, 'user_name') else \
                user_session.user.username


def set_audit_fields(obj, user_session):
    user_name = get_user_name(user_session)
    obj.set_audit_fields(user_name)


def get_entity_field_info(entity: Entity, field_name: str):
    return getattr(entity, field_name, None)


def get_entity_list():
    repository = get_table_repository()
    return repository.__all__


def get_entities():
    repository = get_table_repository()
    return [getattr(repository, table, None) for table in repository.__all__]


def get_field_list(cls):
    return cls.init_field_dict()


async def get_field_values(obj, adict, fields=None):
    adict = await obj.get_field_values(adict, fields) if obj else {key: None for key in adict.keys()}
    return adict


async def set_field_values(adict, obj, fields=None):
    return await obj.set_field_values(adict, fields) if obj else False


async def record_exist(self, table_name: str, *args, **kwargs):
    klass = get_entity(table_name) if isinstance(table_name, str) else table_name
    return await klass.record_exist(*args, **kwargs)


async def validate_existence(self, entity_obj):
    return await entity_obj.validate_existence()


def save_timestamp(cookies, obj):
    return obj.save_timestamp(cookies)


def check_timestamp(cookies, obj):
    obj.check_timestamp(cookies)


async def get_recordset(table_name: str, *args, **kwargs):
    klass = get_entity(table_name) if isinstance(table_name, str) else table_name
    return await klass.get_recordset(*args, **kwargs)


async def get_audit_recordset(table_name: str, *args, **kwargs):
    klass = get_entity(table_name) if isinstance(table_name, str) else table_name
    return await klass.get_audit_recordset(*args, **kwargs)


async def session_close_all(session=None):
    if not session:
        session = Session()
    try:
        try:
            if session.is_active:
                await session.rollback()
        finally:
            # ensuring session were not kept, but removed in multi-threaded environment. As described in
            # http://docs.sqlalchemy.org/en/latest/orm/contextual.html?highlight=scoped#sqlalchemy.orm.scoping.scoped_session.remove
            await session.remove()
    except:
        pass


async def safe_execute(func, *args, **kwargs):
    async with Session() as session:
        async with session.begin():
            try:
                if inspect.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
            finally:
                await session_close_all(session)
    return result
