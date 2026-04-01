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

from artanis.abc.workers.base import BaseWorker

if t.TYPE_CHECKING:
    from artanis.asgi.asgiservice import ASGIService
    from artanis.client import Client

__all__ = ["HTTPWorker"]


class HTTPWorker(BaseWorker):
    """Worker for HTTP client.

    It will provide a artanis Client and create the repositories for the corresponding resources.
    """

    _client: "Client"

    def __init__(self, url: str | t.Callable[[], str], app: "ASGIService | None" = None, **client_kwargs: t.Any):
        super().__init__(app=app)
        self._url = url
        self._client_kwargs = client_kwargs

    @property
    def url(self) -> str:
        return self._url() if callable(self._url) else self._url

    @property
    def client(self) -> "Client":
        """Client to interact with an HTTP resource

        :return: HTTP client.
        :raises AttributeError: If the client is not initialized.
        """
        try:
            return self._client
        except AttributeError:
            raise AttributeError("Client not initialized")

    @client.setter
    def client(self, client: "Client") -> None:
        """Set the client to interact with an HTTP resource.

        :param client: HTTP client.
        """
        self._client = client

    @client.deleter
    def client(self) -> None:
        """Delete the client."""
        del self._client

    async def set_up(self) -> None:
        """Initialize the client with the URL."""
        from artanis.client import Client

        self.client = Client(base_url=self.url, **self._client_kwargs)

        await self.client.__aenter__()

    async def tear_down(self, *, rollback: bool = False) -> None:
        """Close and delete the client.

        :param rollback: If the unit of work should be rolled back.
        """
        await self.client.__aexit__()
        del self.client

    async def repository_params(self) -> tuple[list[t.Any], dict[str, t.Any]]:
        """Get the parameters for initialising the repositories.

        :return: Parameters for initialising the repositories.
        """
        return [self.client], {}

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
