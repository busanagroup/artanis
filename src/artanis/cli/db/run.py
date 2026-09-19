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
import logging
import sys
from types import ModuleType

from tortoise.cli.cli import (
    CLIContext,
    init as tortoise_init,
    makemigrations as tortoise_makemigrations,
    migrate as tortoise_migrate,
)

from artanis.cli.db.args import InitCMDArgs
from artanis.config import Configuration
from artanis.sqlentity.entrypoint import get_dbconfig
from artanis.utils import load_ecf_modules

logger = logging.getLogger(__name__)


def _make_tortoise_cli_context(dbconfig: dict) -> CLIContext:
    module_name = "_artanis_tortoise_config"
    module = ModuleType(module_name)
    module.TORTOISE_ORM = dbconfig
    sys.modules[module_name] = module
    return CLIContext(config=f"{module_name}.TORTOISE_ORM", config_file=None)


async def run_initdb(config):
    cli_context = _make_tortoise_cli_context(config)
    logger.info("Initializing database schema with Tortoise CLI")
    await tortoise_init(cli_context, tuple())
    logger.info("... database initialization completed")


async def db_process(args: InitCMDArgs):
    config = Configuration.get_default_instance(create_instance=False)
    load_ecf_modules("ecf.tbl", True)
    dbconfig = get_dbconfig(config)
    cli_context = _make_tortoise_cli_context(dbconfig)
    app_labels = tuple(args.app_labels)

    if args.subcommand == "init":
        logger.info("Initializing database")
        await tortoise_init(cli_context, app_labels)
    elif args.subcommand == "makemigrations":
        logger.info("Generating migrations for configured apps")
        await tortoise_makemigrations(cli_context, app_labels, empty=False, name=None)
    elif args.subcommand == "migrate":
        app_label = args.app_labels[0] if args.app_labels else None
        migration = args.app_labels[1] if len(args.app_labels) > 1 else None
        logger.info("Applying database migrations")
        await tortoise_migrate(cli_context, app_label, migration, fake=False, dry_run=False)
    else:
        logger.error(f"Unknown subcommand: {args.subcommand}")
