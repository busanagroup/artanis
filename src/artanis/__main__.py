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

import argparse
import sys
from typing import List, Optional

from artanis.config import Configuration
from artanis.server import Artanis


def __load_config(config_path: str | None = None):
    config = Configuration.get_default_instance(config_path=config_path)
    config.configure_logging()
    return config


def main(sys_args: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        help="Location of a config file.",
        default=None,
    )
    args = parser.parse_args(sys_args or sys.argv[1:])
    config = __load_config(args.config)
    server = Artanis(config=config)
    server.start()
    return server.daemonize()


if __name__ == "__main__":
    sys.exit(main())
