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

# types.py
# Copyright (C) 2005-2026 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
from __future__ import annotations

"""Compatibility namespace for sqlalchemy.sql.types."""

# Re-export from SQLAlchemy
from sqlalchemy.engine import create_engine as create_engine  # noqa
from sqlalchemy.engine import create_mock_engine as create_mock_engine  # noqa
from sqlalchemy.engine import engine_from_config as engine_from_config  # noqa
from sqlalchemy.inspection import inspect as inspect  # noqa
from sqlalchemy.pool import QueuePool as QueuePool  # noqa
from sqlalchemy.pool import StaticPool as StaticPool  # noqa
from sqlalchemy.schema import BLANK_SCHEMA as BLANK_SCHEMA  # noqa
from sqlalchemy.schema import DDL as DDL  # noqa
from sqlalchemy.schema import CheckConstraint as CheckConstraint  # noqa
from sqlalchemy.schema import Column as Column  # noqa
from sqlalchemy.schema import ColumnDefault as ColumnDefault  # noqa
from sqlalchemy.schema import Computed as Computed  # noqa
from sqlalchemy.schema import Constraint as Constraint  # noqa
from sqlalchemy.schema import DefaultClause as DefaultClause  # noqa
from sqlalchemy.schema import FetchedValue as FetchedValue  # noqa
from sqlalchemy.schema import ForeignKey as ForeignKey  # noqa
from sqlalchemy.schema import ForeignKeyConstraint as ForeignKeyConstraint  # noqa
from sqlalchemy.schema import Identity as Identity  # noqa
from sqlalchemy.schema import Index as Index  # noqa
from sqlalchemy.schema import MetaData as MetaData  # noqa
from sqlalchemy.schema import PrimaryKeyConstraint as PrimaryKeyConstraint  # noqa
from sqlalchemy.schema import Sequence as Sequence  # noqa
from sqlalchemy.schema import Table as Table  # noqa
from sqlalchemy.schema import UniqueConstraint as UniqueConstraint  # noqa
from sqlalchemy.sql import LABEL_STYLE_DEFAULT as LABEL_STYLE_DEFAULT  # noqa
from sqlalchemy.sql import (  # noqa
    LABEL_STYLE_DISAMBIGUATE_ONLY as LABEL_STYLE_DISAMBIGUATE_ONLY,
)
from sqlalchemy.sql import LABEL_STYLE_NONE as LABEL_STYLE_NONE  # noqa
from sqlalchemy.sql import (  # noqa
    LABEL_STYLE_TABLENAME_PLUS_COL as LABEL_STYLE_TABLENAME_PLUS_COL,
)
from sqlalchemy.sql import alias as alias  # noqa
from sqlalchemy.sql import bindparam as bindparam  # noqa
from sqlalchemy.sql import column as column  # noqa
from sqlalchemy.sql import delete as delete  # noqa
from sqlalchemy.sql import except_ as except_  # noqa
from sqlalchemy.sql import except_all as except_all  # noqa
from sqlalchemy.sql import exists as exists  # noqa
from sqlalchemy.sql import false as false  # noqa
from sqlalchemy.sql import func as func  # noqa
from sqlalchemy.sql import insert as insert  # noqa
from sqlalchemy.sql import intersect as intersect  # noqa
from sqlalchemy.sql import intersect_all as intersect_all  # noqa
from sqlalchemy.sql import join as join  # noqa
from sqlalchemy.sql import lambda_stmt as lambda_stmt  # noqa
from sqlalchemy.sql import lateral as lateral  # noqa
from sqlalchemy.sql import literal as literal  # noqa
from sqlalchemy.sql import literal_column as literal_column  # noqa
from sqlalchemy.sql import modifier as modifier  # noqa
from sqlalchemy.sql import null as null  # noqa
from sqlalchemy.sql import nullsfirst as nullsfirst  # noqa
from sqlalchemy.sql import nullslast as nullslast  # noqa
from sqlalchemy.sql import outerjoin as outerjoin  # noqa
from sqlalchemy.sql import outparam as outparam  # noqa
from sqlalchemy.sql import table as table  # noqa
from sqlalchemy.sql import tablesample as tablesample  # noqa
from sqlalchemy.sql import text as text  # noqa
from sqlalchemy.sql import true as true  # noqa
from sqlalchemy.sql import union as union  # noqa
from sqlalchemy.sql import union_all as union_all  # noqa
from sqlalchemy.sql import update as update  # noqa
from sqlalchemy.sql import values as values  # noqa
from sqlalchemy.types import ARRAY as ARRAY  # noqa
from sqlalchemy.types import BIGINT as BIGINT  # noqa
from sqlalchemy.types import BINARY as BINARY  # noqa
from sqlalchemy.types import BLOB as BLOB  # noqa
from sqlalchemy.types import BOOLEAN as BOOLEAN  # noqa
from sqlalchemy.types import CHAR as CHAR  # noqa
from sqlalchemy.types import CLOB as CLOB  # noqa
from sqlalchemy.types import DATE as DATE  # noqa
from sqlalchemy.types import DATETIME as DATETIME  # noqa
from sqlalchemy.types import DECIMAL as DECIMAL  # noqa
from sqlalchemy.types import DOUBLE as DOUBLE  # noqa
from sqlalchemy.types import DOUBLE_PRECISION as DOUBLE_PRECISION  # noqa
from sqlalchemy.types import FLOAT as FLOAT  # noqa
from sqlalchemy.types import INT as INT  # noqa
from sqlalchemy.types import INTEGER as INTEGER  # noqa
from sqlalchemy.types import JSON as JSON  # noqa
from sqlalchemy.types import NCHAR as NCHAR  # noqa
from sqlalchemy.types import NUMERIC as NUMERIC  # noqa
from sqlalchemy.types import NVARCHAR as NVARCHAR  # noqa
from sqlalchemy.types import REAL as REAL  # noqa
from sqlalchemy.types import SMALLINT as SMALLINT  # noqa
from sqlalchemy.types import TEXT as TEXT  # noqa
from sqlalchemy.types import TIME as TIME  # noqa
from sqlalchemy.types import TIMESTAMP as TIMESTAMP  # noqa
from sqlalchemy.types import UUID as UUID  # noqa
from sqlalchemy.types import VARBINARY as VARBINARY  # noqa
from sqlalchemy.types import VARCHAR as VARCHAR  # noqa
from sqlalchemy.types import BigInteger as BigInteger  # noqa
from sqlalchemy.types import Boolean as Boolean  # noqa
from sqlalchemy.types import Date as Date  # noqa
from sqlalchemy.types import DateTime as DateTime  # noqa
from sqlalchemy.types import Double as Double  # noqa
from sqlalchemy.types import Enum as Enum  # noqa
from sqlalchemy.types import Float as Float  # noqa
from sqlalchemy.types import Integer as Integer  # noqa
from sqlalchemy.types import Interval as Interval  # noqa
from sqlalchemy.types import LargeBinary as LargeBinary  # noqa
from sqlalchemy.types import Numeric as Numeric  # noqa
from sqlalchemy.types import PickleType as PickleType  # noqa
from sqlalchemy.types import SmallInteger as SmallInteger  # noqa
from sqlalchemy.types import String as String  # noqa
from sqlalchemy.types import Text as Text  # noqa
from sqlalchemy.types import Time as Time  # noqa
from sqlalchemy.types import TupleType as TupleType  # noqa
from sqlalchemy.types import TypeDecorator as TypeDecorator  # noqa
from sqlalchemy.types import Unicode as Unicode  # noqa
from sqlalchemy.types import UnicodeText as UnicodeText  # noqa
from sqlalchemy.types import Uuid as Uuid  # noqa

# From SQLModel, modifications of SQLAlchemy or equivalents of Pydantic
from sqlmodel.sql.expression import all_ as all_  # noqa
from sqlmodel.sql.expression import and_ as and_  # noqa
from sqlmodel.sql.expression import any_ as any_  # noqa
from sqlmodel.sql.expression import asc as asc  # noqa
from sqlmodel.sql.expression import between as between  # noqa
from sqlmodel.sql.expression import case as case  # noqa
from sqlmodel.sql.expression import cast as cast  # noqa
from sqlmodel.sql.expression import col as col  # noqa
from sqlmodel.sql.expression import collate as collate  # noqa
from sqlmodel.sql.expression import desc as desc  # noqa
from sqlmodel.sql.expression import distinct as distinct  # noqa
from sqlmodel.sql.expression import extract as extract  # noqa
from sqlmodel.sql.expression import funcfilter as funcfilter  # noqa
from sqlmodel.sql.expression import not_ as not_  # noqa
from sqlmodel.sql.expression import nulls_first as nulls_first  # noqa
from sqlmodel.sql.expression import nulls_last as nulls_last  # noqa
from sqlmodel.sql.expression import or_ as or_  # noqa
from sqlmodel.sql.expression import over as over  # noqa
from sqlmodel.sql.expression import select as select  # noqa
from sqlmodel.sql.expression import tuple_ as tuple_  # noqa
from sqlmodel.sql.expression import type_coerce as type_coerce  # noqa
from sqlmodel.sql.expression import within_group as within_group  # noqa
from sqlmodel.sql.sqltypes import AutoString as AutoString  # noqa

# From SQLEntity, modification of SQLModel for Artanis usage
from .sqlorm import Field as Field
from .sqlorm import Entity as Entity
from .sqlorm import Relationship as Relationship
