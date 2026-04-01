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
import typing

__all__ = ["SchemaError", "SchemaParseError", "SchemaValidationError", "SchemaGenerationError"]


class SchemaError(Exception):
    def __init__(self, errors: str | dict[str, typing.Any], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = errors


class SchemaParseError(SchemaError):
    pass


class SchemaValidationError(SchemaError):
    pass


class SchemaGenerationError(Exception):
    pass
