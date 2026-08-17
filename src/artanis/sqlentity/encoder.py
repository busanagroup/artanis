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
from __future__ import annotations

import decimal
import functools
import json
from typing import Callable, Any


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(str(o))
        return super(self.__class__, self).default(o)


JsonDumpsFunc = Callable[[Any], str]
JsonLoadsFunc = Callable[[str | bytes], Any]

JSON_DUMPS: JsonDumpsFunc = functools.partial(json.dumps, cls=DecimalEncoder, separators=(",", ":"))
JSON_LOADS: JsonLoadsFunc = json.loads
