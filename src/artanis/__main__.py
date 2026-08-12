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


import argparse
import sys
from typing import List, Optional, Dict

from artanis import __version__
from artanis.abc.command import ArtanisCommand
from artanis.config import Configuration
from artanis.utils import import_function


def __load_config(config_path: str | None = None):
    config = Configuration.get_default_instance(config_path=config_path)
    config.configure_logging()
    return config


def main(sys_args: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description= f"Artanis Server version {__version__}",
    )
    parser.add_argument(
        "-v",
        "--version",
        dest="version",
        action="store_true",
        help="print current taskiq version and exit",
    )
    parser.add_argument(
        "-c",
        "--config",
        help="Location of a config file.",
        default=None,
    )
    subcommands: Dict[str, ArtanisCommand] = {}
    subparsers = parser.add_subparsers(
        title="Available subcommands",
        metavar="",
        dest="subcommand",
    )
    command_classes = import_function(f"artanis.cli:__command_classses__")
    for klass in command_classes:
        if issubclass(klass, ArtanisCommand):
            subparsers.add_parser(
                klass.name,
                help=klass.short_help,
                add_help=False,
            )
            subcommands[klass.name] = klass()
    args, _ = parser.parse_known_args()
    if args.version:
        print(__version__)  # noqa: T201
        return 0

    if args.subcommand is None:
        parser.print_help()
        return 0

    if not args.config:
        print("Config file is required. Use -c or --config to specify the config file path.")
        return -1
    __load_config(args.config)


    command = subcommands[args.subcommand]
    sys.argv.pop(0)
    return command.exec(sys.argv[1:]) or 0

if __name__ == "__main__":
    sys.exit(main())
