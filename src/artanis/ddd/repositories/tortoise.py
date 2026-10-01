
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
import typing as t

from artanis import exceptions
from artanis.ddd import exceptions as ddd_exceptions
from artanis.ddd.repositories import BaseRepository
from artanis.sqlentity.sqlorm import Entity

try:
    from tortoise import BaseDBAsyncClient
    from tortoise.exceptions import DoesNotExist, IntegrityError as TortoiseIntegrityError, MultipleObjectsReturned
except Exception:  # pragma: no cover
    raise exceptions.DependencyNotInstalled(dependency="tortoise", dependant=__name__)

__all__ = ["TortoiseRepository", "TortoiseTableManager", "TortoiseTableRepository"]


class TortoiseRepository(BaseRepository):
    """Base class for Tortoise ORM repositories. It provides a connection to the database."""

    def __init__(self, connection: BaseDBAsyncClient, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._connection = connection

    def __eq__(self, other):
        return isinstance(other, TortoiseRepository) and self._connection == other._connection


class TortoiseTableManager:
    def __init__(self, table: type[Entity], connection: BaseDBAsyncClient):  # type: ignore
        self._connection = connection
        self.table = table
        self.resource = table._meta.db_table

    def __eq__(self, other):
        return (
            isinstance(other, TortoiseTableManager)
            and self._connection == other._connection
            and self.table == other.table
        )

    async def create(self, *data: dict[str, t.Any]) -> list[dict[str, t.Any]]:
        """Creates new elements in the table."""
        created: list[dict[str, t.Any]] = []
        for item in data:
            model_data = self._normalize_data(dict(item))
            model = self.table(**model_data)
            try:
                await model.save()
            except TortoiseIntegrityError:
                raise ddd_exceptions.IntegrityError(resource=self.resource)
            created.append(self._model_to_dict(model))
        return created

    async def retrieve(self, *clauses, **filters) -> dict[str, t.Any]:
        """Retrieves a single element from the table."""
        query = self._filter_query(self.table.all(), *clauses, **filters)
        try:
            element = await query.get()
        except DoesNotExist:
            raise ddd_exceptions.NotFoundError(resource=self.resource)
        except MultipleObjectsReturned:
            raise ddd_exceptions.MultipleRecordsError(resource=self.resource)
        return self._model_to_dict(element)

    async def update(self, data: dict[str, t.Any], *clauses, **filters) -> list[dict[str, t.Any]]:
        """Updates matching elements and returns the updated state."""
        query = self._filter_query(self.table.all(), *clauses, **filters)
        existing = await query.all()
        if not existing:
            return []
        pks = [getattr(element, self._pk_field_name()) for element in existing]
        try:
            await query.update(**data)
        except TortoiseIntegrityError:
            raise ddd_exceptions.IntegrityError(resource=self.resource)
        updated = await self.table.filter(**{f"{self._pk_field_name()}__in": pks}).all()
        return [self._model_to_dict(element) for element in updated]

    async def delete(self, *clauses, **filters) -> None:
        """Deletes the matching element(s) from the table."""
        await self.retrieve(*clauses, **filters)
        query = self._filter_query(self.table.all(), *clauses, **filters)
        try:
            await query.delete()
        except TortoiseIntegrityError:
            raise ddd_exceptions.IntegrityError(resource=self.resource)

    async def list(
        self, *clauses, order_by: str | None = None, order_direction: t.Literal["asc", "desc"] = "asc", **filters
    ) -> t.AsyncIterable[dict[str, t.Any]]:
        """Lists all matching elements in the table."""
        query = self._filter_query(self.table.all(), *clauses, **filters)
        if order_by:
            query = query.order_by(f"-{order_by}" if order_direction == "desc" else order_by)
        for element in await query.all():
            yield self._model_to_dict(element)

    async def drop(self, *clauses, **filters) -> int:
        """Deletes all matching elements and returns how many were removed."""
        query = self._filter_query(self.table.all(), *clauses, **filters)
        return await query.delete()

    def _filter_query(self, queryset, *clauses, **filters):
        if clauses or filters:
            return queryset.filter(*clauses, **filters)
        return queryset

    def _pk_field_name(self) -> str:
        return self.table._meta.pk_attr

    def _normalize_data(self, data: dict[str, t.Any]) -> dict[str, t.Any]:
        normalized = dict(data)
        for field_name in self.table._meta.fields:
            if field_name in normalized:
                continue
            field = self.table._meta.fields_map[field_name]
            if field.pk and getattr(field, "generated", False):
                continue
            if field.default is not None:
                default_value = field.default
                normalized[field_name] = default_value() if callable(default_value) else default_value
                continue
            if field.null:
                normalized[field_name] = None
                continue
            if field.__class__.__name__.endswith("BooleanField"):
                normalized[field_name] = False
            elif field.__class__.__name__.endswith(("IntField", "DecimalField")):
                normalized[field_name] = 0
            elif field.__class__.__name__.endswith("CharField"):
                normalized[field_name] = ""
            else:
                normalized[field_name] = None
        return normalized

    @staticmethod
    def _model_to_dict(model: Entity) -> dict[str, t.Any]:
        return {field: getattr(model, field) for field in model._meta.fields}


class TortoiseTableRepository(TortoiseRepository):
    _table: t.ClassVar[type[Entity]]  # type: ignore

    def __init__(self, connection: BaseDBAsyncClient, *args, **kwargs):
        super().__init__(connection, *args, **kwargs)
        self._table_manager = TortoiseTableManager(self._table, connection)

    def __eq__(self, other):
        return isinstance(other, TortoiseTableRepository) and self._table == other._table and super().__eq__(other)

    async def create(self, *data: dict[str, t.Any]) -> list[dict[str, t.Any]]:
        return await self._table_manager.create(*data)

    async def retrieve(self, *clauses, **filters) -> dict[str, t.Any]:
        return await self._table_manager.retrieve(*clauses, **filters)

    async def update(self, data: dict[str, t.Any], *clauses, **filters) -> list[dict[str, t.Any]]:
        return await self._table_manager.update(data, *clauses, **filters)

    async def delete(self, *clauses, **filters) -> None:
        await self._table_manager.delete(*clauses, **filters)

    async def list(
        self, *clauses, order_by: str | None = None, order_direction: t.Literal["asc", "desc"] = "asc", **filters
    ) -> t.AsyncIterable[dict[str, t.Any]]:
        async for element in self._table_manager.list(
            *clauses,
            order_by=order_by,
            order_direction=order_direction,
            **filters,
        ):
            yield element

    async def drop(self, *clauses, **filters) -> int:
        return await self._table_manager.drop(*clauses, **filters)


