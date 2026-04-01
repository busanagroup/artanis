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
# ruff: noqa
import datetime
import typing as t
import uuid

from marshmallow.fields import *

MAPPING: t.Dict[type | None, type[Field]] = {
    None: Field,
    int: Integer,
    float: Float,
    str: String,
    bool: Boolean,
    list: List,
    dict: Dict,
    uuid.UUID: UUID,
    datetime.date: Date,
    datetime.datetime: DateTime,
    datetime.time: Time,
}

MAPPING_TYPES = {v: k for k, v in MAPPING.items()}
