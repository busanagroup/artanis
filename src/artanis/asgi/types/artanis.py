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

import dataclasses

__all__ = ["UserInfo"]


@dataclasses.dataclass(frozen=True)
class UserInfo:
    username: str | None
    username: str | None
    first_name: str | None
    last_name: str | None
    email: str | None
    cono: str | None
    coname: str | None
    dvno: str | None
    dvname: str | None
