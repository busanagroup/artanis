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

from typing import Any, TypeAlias

ChannelRawRedisHost: TypeAlias = (
        dict[str, Any] | tuple[str, int] | list[str | int] | str
)
"""Raw Redis host configuration in various supported formats.

Can be:
- str: "redis://localhost:6379"
- tuple: ("localhost", 6379)
- list: ["localhost", 6379]
- dict: {"host": "localhost", "port": 6379, "db": 0}
"""

ChannelDecodedRedisHost: TypeAlias = dict[str, Any]
"""Decoded Redis host configuration as a standardized dictionary.

Contains normalized Redis connection parameters like host, port, db, etc.
"""

SymmetricEncryptionKeys: TypeAlias = list[str | bytes]
"""List of symmetric encryption keys for message encryption.

Used for encrypting/decrypting messages in Redis channel layers.
Keys can be provided as strings or byte arrays.
"""
