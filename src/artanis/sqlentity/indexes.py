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

from tortoise import Model
from tortoise.indexes import Index as TortoiseIndex
from tortoise.indexes import PartialIndex as TortoisePartialIndex

from artanis.sqlentity.schema_generator import PostgreSQLSchemaGenerator


class Index(TortoiseIndex):

    def get_sql(self, schema_generator: PostgreSQLSchemaGenerator, model: type[Model], safe: bool) -> str:
        self.resolve_expressions(model)
        # This function is required by aerich
        return schema_generator._get_index_sql(
            model,
            self.field_names,
            safe,
            index_name=self.index_name(schema_generator=schema_generator, model=model),
            index_type=self.INDEX_TYPE,
            extra=self.extra,
        )


class PartialIndex(TortoisePartialIndex):

    def get_sql(self, schema_generator: PostgreSQLSchemaGenerator, model: type[Model], safe: bool) -> str:
        self.resolve_expressions(model)
        # This function is required by aerich
        return schema_generator._get_index_sql(
            model,
            self.field_names,
            safe,
            index_name=self.index_name(schema_generator=schema_generator, model=model),
            index_type=self.INDEX_TYPE,
            extra=self.extra,
        )


class UniqueIndex(TortoiseIndex):

    def get_sql(self, schema_generator: PostgreSQLSchemaGenerator, model: type[Model], safe: bool) -> str:
        """
        Generate SQL for creating the index.

        :param schema_generator: Schema generator instance.
        :param model: Model class.
        :param safe: Whether to use "IF NOT EXISTS" in the SQL.
        :return: SQL string for creating the index.
        """
        self.resolve_expressions(model)
        exists = "IF NOT EXISTS " if safe else ""
        return schema_generator._get_artanis_unique_index(
            model,
            self.field_names,
            safe,
            index_name=self.index_name(schema_generator=schema_generator, model=model),
            index_type=self.INDEX_TYPE,
            extra=self.extra
        )
