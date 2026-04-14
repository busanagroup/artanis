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
import abc
from typing import Optional, Any, NamedTuple

from httpx import AsyncClient
from starlette.datastructures import MutableHeaders


class ConnectionHeaderParseResult(NamedTuple):
    require_close: bool
    new_headers: MutableHeaders


class BaseProxy(abc.ABC):
    client: AsyncClient
    follow_redirects: bool

    def __init__(
            self,
            client: Optional[AsyncClient] = None,
            *,
            follow_redirects: bool = False
    ) -> None:
        self.client = client if client is not None else AsyncClient()
        self.follow_redirects = follow_redirects

    async def aclose(self) -> None:
        await self.client.aclose()

    @abc.abstractmethod
    async def send_request_to_target(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()

    @abc.abstractmethod
    async def proxy(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()
