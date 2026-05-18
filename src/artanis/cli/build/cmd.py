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
import asyncio
import logging
from typing import Optional, Sequence

from artanis.abc.command import ArtanisCommand
from artanis.cli.build.run import run_build

logger = logging.getLogger(__name__)


class BuildCMD(ArtanisCommand):
    """Command to Build menu/view definition Server."""

    name: str = "build"

    short_help = "Helper to build/rebuild menu/view definition"

    def exec(self, args: Sequence[str]) -> Optional[int]:
        """
        Start worker process.

        Worker process creates several small
        processes in which tasks are actually processed.

        :param args: CLI arguments.
        :returns: status code.
        """
        logger.info("Running artanis builder")
        asyncio.run(run_build())
        return 0

