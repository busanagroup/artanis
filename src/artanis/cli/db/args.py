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
import typing as t
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from dataclasses import dataclass, field


@dataclass
class InitCMDArgs:
    """Arguments for InitCMD."""

    subcommand: str
    app_labels: t.List[str] = field(default_factory=list)

    @classmethod
    def from_cli(cls, args: t.Optional[t.Sequence[str]] = None) -> "InitCMDArgs":
        """Parse CLI arguments and return an instance of InitCMDArgs."""

        parser = ArgumentParser(
            formatter_class=ArgumentDefaultsHelpFormatter,
            description="Subcommand to run db for Artanis Server.",
        )
        subparsers = parser.add_subparsers(
            title="Available subcommands",
            metavar="",
            dest="subcommand",
        )

        for command_name, help_text in (
            ("init", "Initialize database schema for configured apps."),
            (
                "makemigrations",
                "Generate migration files for configured apps.",
            ),
            (
                "migrate",
                "Apply pending migrations to the configured database.",
            ),
        ):
            command_parser = subparsers.add_parser(command_name, help=help_text)
            command_parser.add_argument("app_labels", nargs="*")

        namespace = parser.parse_args(args)
        if namespace.subcommand is None:
            parser.print_help()
            parser.exit(1)
        return cls(
            subcommand=namespace.subcommand,
            app_labels=getattr(namespace, "app_labels", []),
        )