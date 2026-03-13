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

import datetime as dt

from artanis.component.forbidden import curse


def patch_datetime():
    curse(dt.date, 'tointeger', date_tointeger)
    curse(dt.date, 'frominteger', classmethod(date_tointeger))
    curse(dt.time, 'tointeger', time_tointeger)
    curse(dt.time, 'frominteger', classmethod(time_frominteger))
    curse(dt.datetime, 'tointeger', classmethod(datetime_tointeger))
    curse(dt.datetime, 'frominteger', classmethod(datetime_frominteger))


def perform_patch():
    patch_datetime()


def date_frominteger(cls, n):
    nint = int(n)
    d = int(nint % 100)
    m = int(nint / 100) % 100
    y = int(nint / 10000)
    return cls(y, m, d)


def date_tointeger(self):
    return (self._year * 10000) + (self._month * 100) + self._day


def time_frominteger(cls, n):
    nint = int(n)
    s = int(nint % 100)
    m = int(nint / 100) % 100
    h = int(nint / 10000)
    return cls(h, m, s)


def time_tointeger(self):
    return (self.hour * 10000) + (self.minute * 100) + self.second


def datetime_frominteger(cls, n):
    nlong = int(n)
    s = int(nlong % 100)
    m = int(nlong / 100) % 100
    h = int(nlong / 10000) % 100
    dd = int(nlong / 1000000) % 100
    mm = int(nlong / 100000000) % 100
    yy = int(nlong / 10000000000)
    return cls(yy, mm, dd, h, m, s)


def datetime_fromlong(cls, n):
    nlong = int(n)
    s = int(nlong % 100)
    m = int(nlong / 100) % 100
    h = int(nlong / 10000) % 100
    dd = int(nlong / 1000000) % 100
    mm = int(nlong / 100000000) % 100
    yy = int(nlong / 10000000000)
    return cls(yy, mm, dd, h, m, s)


def datetime_tointeger(self):
    return (self.year * 10000000000) + (self.month * 100000000) + (self.day * 1000000) + \
        (self.hour * 10000) + (self.minute * 100) + self.second


def datetime_tolong(self):
    return self.tointeger()
