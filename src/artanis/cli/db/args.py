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
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from dataclasses import dataclass


@dataclass
class InitCMDArgs:
    """Arguments for InitCMD."""

    subcommand: str

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
        init_parser = subparsers.add_parser(
            "init", help="Create migrations packages for configured apps."
        )
        # init_parser.add_argument("app_labels", nargs="*")
        # init_parser.set_defaults(func=_run_init)

        namespace = parser.parse_args(args)
        return cls(**namespace.__dict__)