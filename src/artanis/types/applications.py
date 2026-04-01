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

import typing as t

if t.TYPE_CHECKING:
    from artanis.asgi.asgiservice import ASGIService
    from artanis.asgi.asgiendpoint import ASGIEndPoint

__all__ = ["is_asgi_instance", "is_endpoint_instance"]


def is_asgi_instance(obj: t.Any) -> t.TypeGuard["ASGIService"]:
    """Checks if an object is an instance of ASGIService.

    :param obj: The object to check.
    :return: True if the object is an instance of ASGIService, False otherwise.
    """
    from artanis.asgi.asgiservice import ASGIService

    return isinstance(obj, ASGIService)


def is_endpoint_instance(obj: t.Any) -> t.TypeGuard["ASGIEndPoint"]:
    """Checks if an object is an instance of ASGIEndPoint.

    :param obj: The object to check.
    :return: True if the object is an instance of ASGIEndPoint, False otherwise.
    """
    from artanis.asgi.asgiendpoint import ASGIEndPoint

    return isinstance(obj, ASGIEndPoint)
