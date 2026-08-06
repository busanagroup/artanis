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
from typing import Any, Self

from tortoise import ConfigurationError
from tortoise import Model as TortoiseModel
from tortoise import ModelMeta as TortoiseMeta
from tortoise.expressions import Q
from tortoise.fields import Field, DecimalField, CharField
from tortoise.queryset import QuerySet

from artanis.sqlentity import PostgreSQLClient
from artanis.sqlentity.fields import UUIDField


class ModelMeta(TortoiseMeta):

    def __new__(cls, name: str, bases: tuple[type, ...], attrs: dict[str, Any]) -> ModelMeta:
        new_class = super().__new__(cls, name, bases, attrs)
        return new_class

    @staticmethod
    def _parse_custom_pk(attrs: dict, pk_attr: str, name: str, is_abstract) -> tuple[dict, str]:

        audit_fields: dict[str, Field] = {
            'audt': DecimalField(max_digits=8, decimal_places=0, label='Audit date'),
            'autm': DecimalField(max_digits=6, decimal_places=0, label='Audit time'),
            'auus': CharField(max_length=24, label='Audit user')
        }
        custom_pk_present = False
        field_prefix: str | None = None

        for key, value in attrs.items():
            if isinstance(value, Field):
                if not field_prefix:
                    field_prefix = key[:4]
                if value.pk:
                    if custom_pk_present:
                        raise ConfigurationError(
                            f"Can't create model {name} with two primary keys,"
                            " only single primary key is supported"
                        )
                    if value.generated and not value.allows_generated:
                        raise ConfigurationError(
                            f"Field '{key}' ({value.__class__.__name__}) can't be DB-generated"
                        )
                    custom_pk_present = True
                    pk_attr = key

        if not custom_pk_present and not is_abstract:
            pk_name = field_prefix + "pkid" if field_prefix else "id"
            if pk_name not in attrs:
                attrs = {pk_name: UUIDField(primary_key=True, null=False), **attrs}
                pk_attr = pk_name

            if not isinstance(attrs[pk_name], Field) or not attrs[pk_name].pk:
                raise ConfigurationError(
                    f"Can't create model {name} without explicit primary key if field '{pk_name}'"
                    " already present"
                )

        if field_prefix:
            for key, value in audit_fields.items():
                field_name = field_prefix + key
                if field_name not in attrs:
                    attrs = {**attrs, field_name: value}

        return attrs, pk_attr


class Entity(TortoiseModel, metaclass=ModelMeta):
    """
    Base class for all entities in the ORM.
    """

    @classmethod
    def get_all(
            cls,
            *args: Q,
            using_db: PostgreSQLClient | None = None,
            **kwargs: Any
    ) -> QuerySet[Self]:
        db_queryset = cls._db_queryset(using_db)
        return db_queryset.filter(*args, **kwargs)

    @classmethod
    async def record_exist(
            cls,
            *args,
            **kwargs
    ) -> tuple[bool, Self | None]:
        obj = await cls.get(*args, **kwargs)
        return (obj is not None), obj

    class Meta:
        abstract = True


