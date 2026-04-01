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

__all__ = ["Worker"]


class Worker(BaseWorker):
    """Worker that does not apply any specific behavior.

    A basic implementation of the worker class that does not apply any specific behavior.
    """

    async def set_up(self) -> None:
        """First step in starting a unit of work."""
        ...

    async def tear_down(self, *, rollback: bool = False) -> None:
        """Last step in ending a unit of work.

        :param rollback: If the unit of work should be rolled back.
        """
        ...

    async def repository_params(self) -> tuple[list[t.Any], dict[str, t.Any]]:
        """Get the parameters for initialising the repositories.

        :return: Parameters for initialising the repositories.
        """
        return [], {}

    async def commit(self) -> None:
        """Commit the unit of work."""
        ...

    async def rollback(self) -> None:
        """Rollback the unit of work."""
        ...
