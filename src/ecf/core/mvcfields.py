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

import operator
import typing as t
from functools import reduce

from tortoise.fields.base import VALUE

CONTROLLER = t.TypeVar("CONTROLLER", bound="MVCService")


class MVCFieldMeta(type):
    """
    Metaclass for MVC fields.
    """

    def __new__(mcs, name: str, bases: tuple[type, ...], attrs: dict) -> type:
        if len(bases) > 1 and bases[0] is MVCFieldBase:
            # Instantiate class with only the 1st base class (should be Field)
            cls = type.__new__(mcs, name, (bases[0],), attrs)
            # All other base classes are our meta types, we store them in class attributes
            field_type = bases[1] if len(bases) == 2 else reduce(operator.or_, bases[1:])
            setattr(cls, "field_type", field_type)
            return cls
        return type.__new__(mcs, name, bases, attrs)


class MVCFieldBase(t.Generic[VALUE], metaclass=MVCFieldMeta):
    """
    Base class for MVC fields.
    """

class ReverseRelation(t.Generic[CONTROLLER]):
    """
    Reverse relation for MVC fields.
    """

    def __init__(self, controller: t.Type[CONTROLLER]):
        self.controller = controller

