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

from typing import TYPE_CHECKING, Sequence

from tortoise import Model
from tortoise.backends.base_postgres.schema_generator import BasePostgresSchemaGenerator

if TYPE_CHECKING:
    pass


class PostgreSQLSchemaGenerator(BasePostgresSchemaGenerator):

    def _get_artanis_unique_index(
            self,
            model: type[Model],
            field_names: Sequence[str],
            safe: bool,
            index_name: str | None = None,
            index_type: str | None = None,
            extra: str | None = None,
    ) -> str:
        """
        Generate SQL for creating a unique index.

        :param model: Model class.
        :param index_name: Name of the index.
        :param field_names: List of field names to include in the index.
        :param safe: Whether to use "IF NOT EXISTS" in the SQL.
        :return: SQL string for creating the unique index.
        """
        if index_type:
            index_type = f"USING {index_type}"
        return self.UNIQUE_INDEX_CREATE_TEMPLATE.format(
            exists="IF NOT EXISTS " if safe else "",
            index_name=index_name or self._get_index_name("uidx", model, field_names),
            index_type=f"{index_type} " if index_type else "",
            table_name=self._qualify_table_name(model._meta.db_table, model._meta.schema),
            fields=self._format_index_fields(field_names),
            extra=f"{extra}" if extra else "",
        )
