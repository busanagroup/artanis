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
import dataclasses
import typing as t

from artanis.ddd.workers.sqlalchemy import SQLAlchemyWorker
from artanis.exceptions import ApplicationError

if t.TYPE_CHECKING:
    from artanis.asgi.asgiservice import ASGIService
    from artanis.ddd.repositories.sqlalchemy import SQLAlchemyTableRepository


@dataclasses.dataclass
class Repositories:
    registered: dict[str, type["SQLAlchemyTableRepository"]] = dataclasses.field(default_factory=dict)
    initialised: dict[str, "SQLAlchemyTableRepository"] | None = None

    def init(self, *args: t.Any, **kwargs: t.Any) -> None:
        self.initialised = {r: cls(*args, **kwargs) for r, cls in self.registered.items()}

    def delete(self) -> None:
        self.initialised = None


class ResourceWorker(SQLAlchemyWorker):
    """The worker used by ASGIService Resources."""

    def __init__(self, app: "ASGIService | None" = None):
        """Initialize the worker.

        This special worker is used to handle the repositories created by ASGIService Resources.

        :param app: The application instance.
        """

        super().__init__(app)
        self._resources_repositories = Repositories()

    def add_repository(self, name: str, repository: type["SQLAlchemyTableRepository"]) -> None:
        """Register a repository.

        :param name: The name of the repository.
        :param repository: The repository class.
        """
        self._resources_repositories.registered[name] = repository

    def remove_repository(self, name: str) -> None:
        """Deregister a repository.

        :param name: The name of the repository.
        """
        del self._resources_repositories.registered[name]

    @property
    def repositories(self) -> dict[str, "SQLAlchemyTableRepository"]:
        """Get the initialized repositories.

        :retirns: The initialized repositories.
        :raises ApplicationError: If the repositories are not initialized.
        """
        if not self._resources_repositories.initialised:
            raise ApplicationError("Repositories not initialized")

        return self._resources_repositories.initialised

    async def begin(self) -> None:
        """Start a unit of work.

        Initialize the connection, begin a transaction, and create the repositories.
        """
        await self.set_up()
        args, kwargs = await self.repository_params()
        self._resources_repositories.init(*args, **kwargs)

    async def end(self, *, rollback: bool = False) -> None:
        """End a unit of work.

        Close the connection, commit or rollback the transaction, and delete the repositories.

        :param rollback: If the unit of work should be rolled back.
        """
        await self.tear_down(rollback=rollback)
        self._resources_repositories.delete()
