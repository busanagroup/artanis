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

import datetime as dt
import typing
from typing import Optional

import sqlalchemy.orm.decl_api as decl_api
from sqlalchemy import orm, schema
from sqlalchemy.orm import declared_attr, InstrumentedAttribute, Query
from sqlalchemy.orm.util import has_identity
from sqlalchemy.sql._typing import _TypeEngineArgument, _T

from artanis.abc.classprops import classproperty
from artanis.config import Configuration


@property
def Session():
    return Configuration.get_default_instance(create_instance=False).container.scoped_session


# -- added by Jaimy for ECF
__internal_field_prefix__ = ['AUCD', 'AUCT', 'AUDT', 'AUTM', 'AUUS', 'KUID']


async def update_or_create_entity(cls, data, surrogate=True):
    mapper = orm.class_mapper(cls)
    pk_props = mapper.primary_key

    # if all pk are present and not None
    if not [1 for p in pk_props if data.get(p.key) is None]:
        record = await cls.query.get([[data[prop.key] for prop in pk_props]])
        if record is None:
            record = cls()
    else:
        if surrogate:
            record = cls()
        else:
            raise Exception("cannot create non surrogate without pk")
    dict_to_entity(record, data)
    return record


def dict_to_entity(entity, data):
    """Update a mapped object with data from a JSON-style nested dict/list
    structure.

    :param entity: the Entity object into which to store the data
    :param data: a `dict` with data to store into the entity
    """

    mapper = orm.object_mapper(entity)

    for key, value in data.items():
        if isinstance(value, dict):
            db_value = getattr(entity, key)
            rel_class = mapper.get_property(key).mapper.class_
            pk_props = orm.class_mapper(rel_class).primary_key

            # If the data doesn't contain any pk, and the relationship
            # already has a value, update that record.
            if not [1 for p in pk_props if p.key in data] and \
                    db_value is not None:
                dict_to_entity(db_value, value)
            else:
                record = update_or_create_entity(rel_class, value)
                setattr(entity, key, record)
        elif isinstance(value, list) and \
                value and isinstance(value[0], dict):

            rel_class = mapper.get_property(key).mapper.class_
            new_attr_value = []
            for row in value:
                if not isinstance(row, dict):
                    raise Exception(
                        'Cannot send mixed (dict/non dict) data '
                        'to list relationships in from_dict data.')
                record = update_or_create_entity(rel_class, row)
                new_attr_value.append(record)
            setattr(entity, key, new_attr_value)
        else:
            setattr(entity, key, value)


def entity_to_dict(entity, deep: dict = {}, exclude: list = []):
    """Generate a JSON-style nested dict/list structure from an object."""

    mapper = orm.object_mapper(entity)

    col_prop_names = [p.key for p in mapper.iterate_properties \
                      if isinstance(p, orm.properties.ColumnProperty)]
    data = dict([(name, getattr(entity, name))
                 for name in col_prop_names if name not in exclude])

    for rname, rdeep in deep.items():
        db_data = getattr(entity, rname)
        prop = mapper.get_property(rname)
        fks = prop.remote_side
        remote_exclude = exclude + [c.name for c in fks]
        if not db_data:
            data[rname] = None
        elif isinstance(db_data, list):
            data[rname] = [entity_to_dict(o, rdeep, remote_exclude) for o in db_data]
        else:
            data[rname] = entity_to_dict(db_data, rdeep, remote_exclude)

    return data


class Base(decl_api.DeclarativeBase):
    pass


class AutogenTable(object):
    __app_config__ = Configuration.get_default_instance(create_instance=False)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def set(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def update_or_create(cls, data, surrogate=True):
        return update_or_create_entity(cls, data, surrogate)

    def from_dict(self, data):
        """
        Update a mapped class with data from a JSON-style nested dict/list
        structure.
        """
        return dict_to_entity(self, data)

    def to_dict(self, deep={}, exclude=[]):
        """Generate a JSON-style nested dict/list structure from an object."""
        return entity_to_dict(self, deep, exclude)

    # session methods
    async def flush(self):
        return orm.object_session(self).flush([self])

    async def delete(self):
        return orm.object_session(self).delete(self)

    async def expire(self, *args, **kwargs):
        return orm.object_session(self).expire(self, *args, **kwargs)

    async def refresh(self, *args, **kwargs):
        return orm.object_session(self).refresh(self, *args, **kwargs)

    async def expunge(self):
        return orm.object_session(self).expunge(self)

    @classproperty
    def query(cls):
        return Query(cls, Session())

    @classmethod
    async def get_by(cls, **kwargs):
        """
        Returns the first instance of this class matching the given criteria.
        This is equivalent to:
        session.query(MyClass).filter_by(...).first()
        """
        result = await Session().execute(Query(cls).filter_by(**kwargs))
        return result.first()

    @classmethod
    async def get(cls, *args):
        """
        Return the instance of this class based on the given identifier,
        or None if not found. This is equivalent to:
        session.query(MyClass).get(...)
        """
        return await Session().get(cls, args)

    @classmethod
    async def get_all(cls, **kwargs):
        result = await Session().execute(Query(cls).filter_by(**kwargs))
        return result

    # -- added by Jaimy Azle for ECF purpose ---
    @classmethod
    def get_field_names(cls, audit=False):
        return [name for name, value in cls.__dict__.items() if isinstance(value, InstrumentedAttribute) and (
                ((audit is False) and (name[-4:] not in __internal_field_prefix__)) or
                ((audit is True) and (name[-4:] in __internal_field_prefix__)))]

    @classmethod
    def get_field_list(cls, audit=False):
        return [value for name, value in cls.__dict__.items() if isinstance(value, InstrumentedAttribute) and (
                ((audit is False) and (name[-4:] not in __internal_field_prefix__)) or
                ((audit is True) and (name[-4:] in __internal_field_prefix__)))]

    @classmethod
    def has_field(cls, field_name):
        return (field_name in cls.__dict__.keys()) and isinstance(cls.__dict__[field_name], InstrumentedAttribute)

    @classmethod
    def init_field_dict(cls, audit=False):
        field_list = cls.get_field_names(audit)
        return {key: None for key in field_list}

    @classmethod
    def get_unmapped_fields(cls, fields: dict):
        cls_fields = cls.init_field_dict()
        return dict([(key, value) for key, value in fields.items() if key not in cls_fields])

    async def get_field_values(self, adict: dict, fields: list = None):
        field_list = adict.keys() if fields is None else fields
        adict.update({key: getattr(self, key, None) for key in field_list \
                      if key[-4:] not in __internal_field_prefix__})
        return adict

    def set_field_values(self, adict: dict, fields: list = None):
        field_list = self.get_field_names() if fields is None else fields
        valid_keys = [key for key in adict.keys() if (key in field_list) and \
                      (getattr(self, key, None) != adict[key])]
        for key in valid_keys:
            setattr(self, key, adict[key])
        return (not valid_keys) == False

    @classmethod
    async def record_exist(cls, *args, **kwargs):
        obj = await cls.get(*args, **kwargs)
        return (obj is not None), obj

    async def validate_existence(self):
        klass: typing.Type[Base] = self.__class__
        fields = [col.name for col in klass.__dict__.values() \
                  if isinstance(col, InstrumentedAttribute) and col.primary_key]
        keys = [getattr(self, key, None) for key in fields if hasattr(self, key)]
        ret_val = (len(fields) == len(keys))
        data = await self.record_exist(keys) if ret_val else (False, None)
        return data[0]

    @classmethod
    async def get_recordset(cls, *args, **kwargs):
        data = await cls.record_exist(*args, **kwargs)
        return_val = cls.init_field_dict()
        return data[1].get_field_values(return_val) if data[0] == True else return_val

    @classmethod
    async def get_audit_recordset(cls, *args, **kwargs):
        data = await cls.record_exist(*args, **kwargs)
        field_list = cls.get_field_names(True)
        return_val = {key: None for key in field_list}
        if data[0]:
            return_val.update({key: getattr(data[1], key, None) for key in field_list})
        return return_val

    def save_timestamp(self, cookies):
        field_list = self.get_field_names(True)
        cookies.update({key[-4:]: getattr(self, key, None) for key in field_list})
        return cookies

    def check_timestamp(self, cookies):
        field_list = self.get_field_names(True)
        field_list = [(key[-4:], key) for key in field_list]
        field_dict = dict(field_list)

        # continue only if history was not an empty dictionary
        chusr = getattr(self, field_dict['AUUS'], None) if 'AUUS' in field_dict else None
        if chusr is not None:
            field_vals = [(cookies[key[0]], getattr(self, key[1], None)) for key in field_list if key[0] != 'AUUS']
            field_vals = [(int(item[0]) if item[0] is not None else item[0], int(item[1]) \
                if item[1] is not None else item[1]) for item in field_vals]
            field_vals = [item[0] == item[1] for item in field_vals]
            is_valid = (False in field_vals) is False
            validators.Assertion(messages={'assert': 'Record has been changed by '
                                                     'user "%s" since last retrieve' % str(chusr)}). \
                to_python(is_valid)

    def set_audit_fields(self, user_name):
        now = dt.datetime.now()
        _has_identity = has_identity(self)

        field_dict = {name[-4:]: name for name in self.get_field_names(True) if name[-4:] in __internal_field_prefix__}
        for key in field_dict.keys():
            value = now.date().tointeger() if key in ['AUCD', 'AUDT'] \
                else now.time().tointeger() if key in ['AUCT', 'AUTM'] \
                else user_name if key == 'AUUS' else None
            if (not _has_identity) and (key in ['AUCD', 'AUCT']) and (value != None):
                setattr(self, field_dict[key], value)
            elif (key in ['AUDT', 'AUTM', 'AUUS']) and (value is not None):
                setattr(self, field_dict[key], value)


class Entity(Base, AutogenTable):
    __abstract__ = True

    def __init_subclass__(cls, **kwargs):
        for key, value in cls.__dict__.items():
            if isinstance(value, InstrumentedAttribute):
                value.key = value.name = key.lower()
        cls.metadata = cls.__app_config__.container.db_metadata
        super().__init_subclass__(**kwargs)


class Field(schema.Column):
    inherit_cache = True

    def __init__(self, type_: Optional[_TypeEngineArgument[_T]], *args, label: str = None, **kwargs):
        super().__init__(type_, *args, **kwargs)
        self.label = label
