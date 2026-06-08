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

from collections.abc import Mapping, Set
from typing import (
    Optional,
    Any,
    TypeVar, Literal
)

# Re-export from SQLAlchemy
from sqlalchemy import orm
from sqlalchemy.ext.asyncio import async_object_session
from sqlalchemy.schema import Column as Column
from sqlalchemy.schema import Sequence as Sequence
from sqlalchemy.sql._typing import _TypeEngineArgument
from sqlmodel import SQLModel, Field as SQLModelField, Relationship as SQLModelRelationship
from sqlmodel._compat import (  # type: ignore[attr-defined]
    PYDANTIC_MINOR_VERSION,
    BaseConfig,
    ModelMetaclass,
    Representation,
    SQLModelConfig,
    Undefined,
    UndefinedType,
    finish_init,
    get_annotations,
    get_field_metadata,
    get_model_fields,
    get_relationship_to,
    get_sa_type_from_field,
    init_pydantic_private_attrs,
    is_field_noneable,
    is_table_model_class,
    sqlmodel_init,
    sqlmodel_validate,
)
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.main import (
    NoArgAnyCallable,
    OnDeleteType,
)
from sqlmodel.sql._expression_select_cls import Select, SelectOfScalar
from sqlmodel.sql.expression import select as select

from artanis.component.validators import validators
from artanis.config import Configuration

_T = TypeVar("_T", bound="Any")

Session: AsyncSession = None  # type: ignore[assignment]

# -- added by Jaimy for ECF
__internal_field_prefix__ = ['audt', 'autm', 'auus', 'kuid']


class Entity(SQLModel):
    """Base class for SQLModel entities."""
    __app_config__: Configuration = Configuration.get_default_instance(create_instance=False)
    __abstract__ = True

    def __init_subclass__(cls, **kwargs):
        if not cls.__app_config__:
            cls.__app_config__ = Configuration.get_default_instance(create_instance=False)
        cls.metadata = cls.__app_config__.container.db_metadata
        super().__init_subclass__(**kwargs)

    def from_dict(self, data):
        """
        Update a mapped class with data from a JSON-style nested dict/list
        structure.
        """
        dict_to_entity(self, data)

    def to_dict(self, deep=None, exclude=None):
        """Generate a JSON-style nested dict/list structure from an object."""
        exclude = exclude or []
        deep = deep or {}
        return entity_to_dict(self, deep, exclude)

    # session methods
    async def flush(self):
        await async_object_session(self).flush([self])

    async def delete(self):
        await async_object_session(self).delete(self)

    async def expire(self, *args, **kwargs):
        async_object_session(self).expire(self, *args, **kwargs)

    async def refresh(self, *args, **kwargs):
        await async_object_session(self).refresh(self, *args, **kwargs)

    async def expunge(self):
        async_object_session(self).expunge(self)

    @classmethod
    def get_query(cls) -> Select | SelectOfScalar:
        return select(cls)

    @classmethod
    async def get_by(cls, **kwargs):
        """
        Returns the first instance of this class matching the given criteria.
        This is equivalent to:
        session.query(MyClass).filter_by(...).first()
        """
        result = await Session().execute(select(cls).filter_by(**kwargs))
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
        result = await Session().exec(select(cls).filter_by(**kwargs))
        return result

    # -- added by Jaimy Azle for ECF purpose ---
    @classmethod
    def get_field_names(cls, audit=False):
        return [name for name in cls.__table__.columns.keys() if
                ((audit is False) and (name[-4:] not in __internal_field_prefix__)) or
                ((audit is True) and (name[-4:] in __internal_field_prefix__))]

    @classmethod
    def get_pk_field_names(cls):
        return [name for name, value in cls.__table__.columns.items() if value.primary_key is True]

    @classmethod
    def get_field_list(cls, audit=False):
        return [value for name, value in cls.__table__.columns.items() if isinstance(value, Column) and (
                ((audit is False) and (name[-4:] not in __internal_field_prefix__)) or
                ((audit is True) and (name[-4:] in __internal_field_prefix__)))]

    @classmethod
    def has_field(cls, field_name):
        return (field_name in cls.__table__.columns.keys()) and isinstance(cls.__table__.columns[field_name], Column)

    @classmethod
    def init_field_dict(cls, audit=False):
        field_list = cls.get_field_names(audit)
        return {key: None for key in field_list}

    @classmethod
    def get_unmapped_fields(cls, fields: dict):
        cls_fields = cls.init_field_dict()
        return dict([(key, value) for key, value in fields.items() if key not in cls_fields])

    def get_field_values(self, adict: dict, fields: list = None):
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
    async def record_exist(cls, *args):
        obj = await cls.get(*args)
        return (obj is not None), obj

    async def validate_existence(self):
        pk_fields = self.get_pk_field_names()
        keys = [getattr(self, key, None) for key in pk_fields if hasattr(self, key)]
        ret_val = (len(pk_fields) == len(keys))
        data = await self.record_exist(keys) if ret_val else [None] * 2
        return data[0]

    @classmethod
    async def get_recordset(cls, *args):
        data = await cls.record_exist(*args)
        return_val = cls.init_field_dict()
        return data[1].get_field_values(return_val) if data[0] == True else return_val

    @classmethod
    async def get_audit_recordset(cls, *args):
        data = await cls.record_exist(*args)
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
        chusr = getattr(self, field_dict['auus'], None) if 'auus' in field_dict else None
        if chusr is not None:
            field_vals = [(cookies[key[0]], getattr(self, key[1], None)) for key in field_list if key[0] != 'auus']
            field_vals = [(int(item[0]) if item[0] is not None else item[0], int(item[1]) \
                if item[1] is not None else item[1]) for item in field_vals]
            field_vals = [item[0] == item[1] for item in field_vals]
            is_valid = (False in field_vals) is False
            validators.Assertion(messages={'assert': 'Record has been changed by '
                                                     'user "%s" since last retrieve' % str(chusr)}). \
                to_python(is_valid)

    def set_audit_fields(self, user_name):
        now = dt.datetime.now()
        _has_identity = orm.util.has_identity(self)

        field_dict = {name[-4:]: name for name in self.get_field_names(True) if name[-4:] in __internal_field_prefix__}
        for key in field_dict.keys():
            value = now.date().tointeger() if key in ['aucd', 'audt'] \
                else now.time().tointeger() if key in ['auct', 'autm'] \
                else user_name if key == 'auus' else None
            if (not _has_identity) and (key in ['aucd', 'auct']) and (value != None):
                setattr(self, field_dict[key], value)
            elif (key in ['audt', 'autm', 'auus']) and (value is not None):
                setattr(self, field_dict[key], value)


def Relationship(
        *,
        back_populates: str | None = None,
        cascade_delete: bool | None = False,
        passive_deletes: bool | Literal["all"] | None = False,
        link_model: Any | None = None,
        sa_relationship: orm.RelationshipProperty[Any] | None = None,
        sa_relationship_args: Sequence[Any] | None = None,
        sa_relationship_kwargs: Mapping[str, Any] | None = None,
) -> Any:
    return SQLModelRelationship(
        back_populates=back_populates,
        cascade_delete=cascade_delete,
        passive_deletes=passive_deletes,
        link_model=link_model,
        sa_relationship=sa_relationship,
        sa_relationship_args=sa_relationship_args,
        sa_relationship_kwargs=sa_relationship_kwargs,
    )


def Field(
        col_type: Optional[_TypeEngineArgument[_T]],
        *,
        default: Any = Undefined,
        default_factory: NoArgAnyCallable | None = None,
        alias: str | None = None,
        validation_alias: str | None = None,
        serialization_alias: str | None = None,
        label: str | None = None,
        title: str | None = None,
        description: str | None = None,
        exclude: Set[int | str] | Mapping[int | str, Any] | Any = None,
        include: Set[int | str] | Mapping[int | str, Any] | Any = None,
        const: bool | None = None,
        gt: float | None = None,
        ge: float | None = None,
        lt: float | None = None,
        le: float | None = None,
        multiple_of: float | None = None,
        max_digits: int | None = None,
        decimal_places: int | None = None,
        min_items: int | None = None,
        max_items: int | None = None,
        unique_items: bool | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        allow_mutation: bool = True,
        regex: str | None = None,
        discriminator: str | None = None,
        repr: bool = True,
        primary_key: bool | UndefinedType = Undefined,
        foreign_key: Any = Undefined,
        ondelete: OnDeleteType | UndefinedType = Undefined,
        unique: bool | UndefinedType = Undefined,
        nullable: bool | UndefinedType = Undefined,
        index: bool | UndefinedType = Undefined,
        sa_column: Column | UndefinedType = Undefined,  # type: ignore
        sa_column_args: Sequence[Any] | UndefinedType = Undefined,
        sa_column_kwargs: Mapping[str, Any] | UndefinedType = Undefined,
        schema_extra: dict[str, Any] | None = None,
) -> Any:
    title = title or label
    return SQLModelField(default,
                         default_factory=default_factory,
                         alias=alias,
                         validation_alias=validation_alias,
                         serialization_alias=serialization_alias,
                         title=title,
                         description=description,
                         exclude=exclude,
                         include=include,
                         const=const,
                         gt=gt,
                         ge=ge,
                         lt=lt,
                         le=le,
                         multiple_of=multiple_of,
                         max_digits=max_digits,
                         decimal_places=decimal_places,
                         min_items=min_items,
                         max_items=max_items,
                         unique_items=unique_items,
                         min_length=min_length,
                         max_length=max_length,
                         allow_mutation=allow_mutation,
                         regex=regex,
                         discriminator=discriminator,
                         repr=repr,
                         primary_key=primary_key,
                         foreign_key=foreign_key,
                         ondelete=ondelete,
                         unique=unique,
                         nullable=nullable,
                         index=index,
                         sa_type=col_type,
                         sa_column=sa_column,
                         sa_column_args=sa_column_args,
                         sa_column_kwargs=sa_column_kwargs,
                         schema_extra=schema_extra)


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


def entity_to_dict(entity, deep=None, exclude=None):
    """Generate a JSON-style nested dict/list structure from an object."""

    exclude = exclude or []
    deep = deep or {}
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
