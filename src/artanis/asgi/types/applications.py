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
import enum
import typing as t

if t.TYPE_CHECKING:
    from artanis.asgi.asgibase import BaseASGIService
    from artanis.asgi.routing import Router


__all__ = ["AppStatus", "is_asgi_instance", "is_router_instance"]


class AppStatus(enum.Enum):
    NOT_STARTED = enum.auto()
    STARTING = enum.auto()
    READY = enum.auto()
    SHUTTING_DOWN = enum.auto()
    SHUT_DOWN = enum.auto()
    FAILED = enum.auto()


def is_asgi_instance(obj: t.Any) -> t.TypeGuard["BaseASGIService"]:
    """Checks if an object is an instance of Artanis.

    :param obj: The object to check.
    :return: True if the object is an instance of Artanis, False otherwise.
    """
    from artanis.asgi.asgibase import BaseASGIService

    return isinstance(obj, BaseASGIService)


def is_router_instance(obj: t.Any) -> t.TypeGuard["Router"]:
    """Checks if an object is an instance of Artanis's Router.

    :param obj: The object to check.
    :return: True if the object is an instance of Router, False otherwise.
    """
    from artanis.asgi.routing import Router

    return isinstance(obj, Router)
