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
import logging
import typing as t

from tortoise import BaseDBAsyncClient, Tortoise

from artanis.ddd.workers.base import BaseWorker

__all__ = ["TortoiseWorker"]

logger = logging.getLogger(__name__)


class TortoiseWorker(BaseWorker):
    """Worker for Tortoise ORM.

    It will provide a connection and a transaction to the database and create the repositories for the entities.
    """

    _connection: BaseDBAsyncClient
    _transaction: t.Any

    @property
    def connection(self) -> BaseDBAsyncClient:
        """Connection to the database.

        :return: Connection to the database.
        :raises AttributeError: If the connection is not initialized.
        """
        try:
            return self._connection
        except AttributeError:
            raise AttributeError("Connection not initialized")

    @connection.setter
    def connection(self, connection: BaseDBAsyncClient) -> None:
        """Set the connection to the database.

        :param connection: Connection to the database.
        """
        self._connection = connection

    @connection.deleter
    def connection(self) -> None:
        """Delete the connection to the database."""
        del self._connection

    @property
    def transaction(self):
        """Open database transaction.

        :return: The active transaction wrapper.
        :raises AttributeError: If the transaction is not started.
        """
        try:
            return self._transaction
        except AttributeError:
            raise AttributeError("Transaction not started")

    @transaction.setter
    def transaction(self, transaction: t.Any) -> None:
        """Set the transaction.

        :param transaction: Current transaction wrapper or context.
        """
        self._transaction = transaction

    @transaction.deleter
    def transaction(self) -> None:
        """Delete the transaction."""
        del self._transaction

    async def set_up(self) -> None:
        """Open the default database connection and begin a transaction."""
        self.connection = Tortoise.get_connection("default")
        transaction_context = self.connection._in_transaction()
        self.transaction = await transaction_context.__aenter__()
        self._transaction_context = transaction_context

    async def tear_down(self, *, rollback: bool = False) -> None:
        """End the transaction and close the connection.

        :param rollback: If the transaction should be rolled back.
        :raises AttributeError: If the connection is not initialized or the transaction is not started.
        """
        if not getattr(self.transaction, "_finalized", False):
            if rollback:
                await self.transaction.rollback()
            else:
                await self.transaction.commit()

        await self._transaction_context.__aexit__(None, None, None)

        del self.transaction
        del self._transaction_context
        del self.connection

    async def repository_params(self) -> tuple[list[t.Any], dict[str, t.Any]]:
        """Get the parameters for initializing the repositories.

        :return: Parameters for initializing the repositories.
        """
        return [self.connection], {}

    async def commit(self):
        """Commit the unit of work."""
        await self.transaction.commit()

    async def rollback(self):
        """Rollback the unit of work."""
        await self.transaction.rollback()


