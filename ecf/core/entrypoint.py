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

from artanis import utils
from artanis.component.rdbms import configure_database, setup_all, unconfigure_database
from artanis.config import Configuration


def load_modules():
    utils.load_ecf_modules("ecf.tbl", True)
    utils.load_ecf_modules("ecf.bo", True)


async def do_startup():
    config = Configuration.get_default_instance(create_instance=False)
    await configure_database(config)
    load_modules()
    await setup_all(config, True)


async def do_shutdown():
    config: Configuration | None = Configuration.get_default_instance(create_instance=False)
    await unconfigure_database(config)
