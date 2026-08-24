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

from artanis.broadcast.defs import ChannelApplication, ChannelScope, ASGIReceiveCallable, ASGISendCallable


class BaseMiddleware:
    """
    Base class for implementing ASGI middleware.

    Note that subclasses of this are not self-safe; don't store state on
    the instance, as it serves multiple application instances. Instead, use
    scope.
    """

    def __init__(self, inner: ChannelApplication):
        """
        Middleware constructor - just takes inner application.

        Args:
            inner: The inner ASGI application to wrap.
        """
        self.inner: ChannelApplication = inner

    async def __call__(
            self, scope: ChannelScope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> ChannelApplication:
        """
        ASGI application; can insert things into the scope and run asynchronous
        code.

        Args:
            scope: The ASGI scope dictionary.
            receive: ASGI receive callable.
            send: ASGI send callable.

        Returns:
            The result of calling the inner application.
        """
        # Copy scope to stop changes going upstream
        scope = dict(scope)
        # Run the inner application along with the scope
        return await self.inner(scope, receive, send)  # type: ignore
