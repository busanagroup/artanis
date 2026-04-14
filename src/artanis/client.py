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
import asyncio
import functools
import logging
import typing as t
from types import TracebackType

from artanis import exceptions
from artanis.asgi import types

if t.TYPE_CHECKING:
    from artanis.asgi.asgibase import BaseASGIService

try:
    import httpx
    from httpx import HTTPError, HTTPStatusError
except Exception:  # pragma: no cover
    raise exceptions.DependencyNotInstalled(
        dependency=exceptions.DependencyNotInstalled.Dependency.httpx, dependant=__name__
    )

__all__ = ["Client", "LifespanContextManager", "HTTPError", "HTTPStatusError"]

logger = logging.getLogger(__name__)


class LifespanContextManager:
    def __init__(self, app: "BaseASGIService", timeout: float = 60.0):
        self.app = app
        self.timeout = timeout
        self._startup_complete = asyncio.Event()
        self._shutdown_complete = asyncio.Event()
        self._receive_queue = asyncio.Queue(maxsize=2)
        self._exception: BaseException | None = None

    async def _startup(self) -> None:
        await self._receive_queue.put(types.Message({"type": "lifespan.startup"}))
        await asyncio.wait_for(self._startup_complete.wait(), timeout=self.timeout)
        if self._exception:
            raise self._exception

    async def _shutdown(self) -> None:
        await self._receive_queue.put(types.Message({"type": "lifespan.shutdown"}))
        await asyncio.wait_for(self._shutdown_complete.wait(), timeout=self.timeout)

    async def _receive(self) -> types.Message:
        return await self._receive_queue.get()

    async def _send(self, message: types.Message) -> None:
        if message["type"] == "lifespan.startup.complete":
            self._startup_complete.set()
        elif message["type"] == "lifespan.shutdown.complete":
            self._shutdown_complete.set()

    async def _app_task(self) -> None:
        scope = types.Scope({"type": "lifespan"})

        try:
            await self.app(scope, self._receive, self._send)
        except BaseException as exc:
            self._exception = exc
            self._startup_complete.set()
            self._shutdown_complete.set()

            raise

    async def __aenter__(self) -> "LifespanContextManager":
        task = asyncio.create_task(self._app_task())

        try:
            await self._startup()
        except BaseException:
            raise
        finally:
            await task

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: TracebackType | None = None,
    ):
        task = asyncio.create_task(self._app_task())

        try:
            await self._shutdown()
        except BaseException:
            raise
        finally:
            await task


class _BaseClient(httpx.AsyncClient):
    def __init__(self, /, **kwargs):
        kwargs.setdefault("base_url", "http://localapp")
        kwargs["headers"] = {"user-agent": f"artanis/1.0", **kwargs.get("headers", {})}

        super().__init__(**kwargs)

    async def __aenter__(self) -> "_BaseClient":
        await super().__aenter__()

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: TracebackType | None = None,
    ):
        await super().__aexit__(exc_type, exc_value, traceback)


class _AppClient(_BaseClient):
    def __init__(self, /, app: "BaseASGIService", **kwargs):
        self.lifespan = LifespanContextManager(app)
        self.app = app

        kwargs.setdefault("transport", httpx.ASGITransport(app=app))  # type: ignore

        super().__init__(**kwargs)

    async def __aenter__(self) -> "_AppClient":
        await self.lifespan.__aenter__()
        await super().__aenter__()

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: TracebackType | None = None,
    ):
        await super().__aexit__(exc_type, exc_value, traceback)
        await self.lifespan.__aexit__(exc_type, exc_value, traceback)


class Client(httpx.AsyncClient):
    """A client for interacting with a ASGIService application either remote or local.

    This client can handle a local python object:
    >>> client = Client(app=ASGIService())

    Or connect to a remote API:
    >>> client = Client(base_url="https://foo.bar")

    Or generate a ASGIService application based on a set of flm model files:
    >>> client = Client(models=[("foo", "/foo/", "model_foo.flm"), ("bar", "/bar/", "model_bar.flm")])

    For initializing the application it's required to use it as an async context manager:
    >>> async with Client(app=ASGIService()) as client:
    >>>     client.post(...)
    """

    @t.overload
    def __init__(self, /, *, app: None = None, models: None = None, **kwargs): ...
    @t.overload
    def __init__(self, /, *, app: "BaseASGIService", **kwargs): ...
    @t.overload
    def __init__(self, /, *, models: t.Sequence[tuple[str, str, str]], **kwargs): ...
    def __init__(
        self,
        /,
        *,
        app: "BaseASGIService | None" = None,
        models: t.Sequence[tuple[str, str, str]] | None = None,
        **kwargs,
    ):
        if models:
            app = BaseASGIService(schema=None, docs=None) if not app else app
            for name, url, path in models:
                app.models.add_model(url, path, name)

        self.lifespan = LifespanContextManager(app) if app else None
        self.app = app
        self.models: dict[str, str] = {m[0]: m[1] for m in models or {}}

        kwargs.setdefault("transport", httpx.ASGITransport(app=app) if app else None)  # type: ignore
        kwargs.setdefault("base_url", "http://localapp")
        kwargs["headers"] = {"user-agent": f"artanis/1.0", **kwargs.get("headers", {})}

        super().__init__(**kwargs)

    async def __aenter__(self) -> "Client":
        if self.lifespan:
            await self.lifespan.__aenter__()
        await super().__aenter__()

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: TracebackType | None = None,
    ):
        await super().__aexit__(exc_type, exc_value, traceback)
        if self.lifespan:
            await self.lifespan.__aexit__(exc_type, exc_value, traceback)

    def model_request(self, model: str, method: str, url: str, **kwargs) -> t.Awaitable[httpx.Response]:
        try:
            m = self.models[model]
        except KeyError:
            raise exceptions.NotFoundException()

        return self.request(method, f"{m.rstrip('/')}{url}", **kwargs)

    model_inspect = functools.partialmethod(model_request, method="GET", url="/")
    model_predict = functools.partialmethod(model_request, method="POST", url="/predict/")
