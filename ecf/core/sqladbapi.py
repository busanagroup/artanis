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

from typing import Any

from sqlalchemy.sql.type_api import TypeEngine


class SQLATypeHelper:

    @classmethod
    def ARRAY_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return None

    @classmethod
    def BIGINT_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.BIGINT

    @classmethod
    def BigInteger_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.BIGINT

    @classmethod
    def BINARY_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.BINARY

    @classmethod
    def BLOB_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.BINARY

    @classmethod
    def BOOLEAN_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.BOOLEAN

    @classmethod
    def Boolean_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.BOOLEAN

    @classmethod
    def CHAR_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.CHAR

    @classmethod
    def CLOB_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.CLOB

    @classmethod
    def Concatenable_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return None

    @classmethod
    def DATE_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.DATE

    @classmethod
    def Date_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.Date

    @classmethod
    def DATETIME_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.DATETIME

    @classmethod
    def DateTime_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.DateTime

    @classmethod
    def DECIMAL_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.DECIMAL

    @classmethod
    def DOUBLE_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.DOUBLE

    @classmethod
    def Double_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.Double

    @classmethod
    def DOUBLE_PRECISION_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.DOUBLE_PRECISION

    @classmethod
    def Enum_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return None

    @classmethod
    def FLOAT_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.FLOAT

    @classmethod
    def Float_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.Float

    @classmethod
    def Indexable_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return None

    @classmethod
    def INT_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.INT

    @classmethod
    def INTEGER_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.INTEGER

    @classmethod
    def Integer_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.Integer

    @classmethod
    def Interval_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return None

    @classmethod
    def JSON_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.CLOB

    @classmethod
    def LargeBinary_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.BINARY

    @classmethod
    def MatchType_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return None

    @classmethod
    def NCHAR_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.CHAR

    @classmethod
    def NULLTYPE_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return None

    @classmethod
    def NullType_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return None

    @classmethod
    def NUMERIC_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.NUMERIC

    @classmethod
    def Numeric_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.Numeric

    @classmethod
    def NVARCHAR_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.VARCHAR

    @classmethod
    def PickleType_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return None

    @classmethod
    def REAL_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.DOUBLE

    @classmethod
    def SchemaType_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return None

    @classmethod
    def SMALLINT_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.SMALLINT

    @classmethod
    def SmallInteger_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.SMALLINT

    @classmethod
    def String_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.STRING

    @classmethod
    def STRINGTYPE_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return None

    @classmethod
    def TEXT_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.TEXT

    @classmethod
    def Text_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.TEXT

    @classmethod
    def TIME_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.TIME

    @classmethod
    def Time_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.TIME

    @classmethod
    def TIMESTAMP_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.TIMESTAMP

    @classmethod
    def TupleType_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return None

    @classmethod
    def Unicode_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.STRING

    @classmethod
    def UnicodeText_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.TEXT

    @classmethod
    def UUID_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return None

    @classmethod
    def Uuid_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return None

    @classmethod
    def VARBINARY_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.BINARY

    @classmethod
    def VARCHAR_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        return dbapi.VARCHAR

    @classmethod
    def get_ecf_type(cls, instance: TypeEngine, dbapi: Any) -> str | None:
        func_name = f'{instance.__name__}_ecf_type' if isinstance(instance, type) \
            else f'{instance.__class__.__name__}_ecf_type'
        func = getattr(cls, func_name, None)
        return func(instance, dbapi) if callable(func) else None
