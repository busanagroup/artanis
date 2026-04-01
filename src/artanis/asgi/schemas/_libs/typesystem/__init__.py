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
import typesystem
from typesystem import Schema
from typesystem.fields import Field

from artanis.asgi.schemas._libs.typesystem import fields, schemas
from artanis.asgi.schemas._libs.typesystem.adapter import TypesystemAdapter

lib = typesystem
adapter = TypesystemAdapter()

__all__ = ["Field", "Schema", "fields", "adapter", "lib", "schemas"]
