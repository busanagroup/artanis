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
import inspect
import typing as t

from artanis import types
from artanis.asgi.pagination import paginators
from artanis.asgi.pagination.paginators.base import BasePaginator

__all__ = ["paginator"]

P = t.ParamSpec("P")
R = t.TypeVar("R", covariant=True)


class Paginator:
    PAGINATORS: dict[types.Pagination, type[BasePaginator]] = {
        "limit_offset": paginators.LimitOffsetPaginator,
        "page_number": paginators.PageNumberPaginator,
    }

    def __init__(self):
        self.schemas: dict[str, t.Any] = {}

    def apply(
            self,
            pagination: types.Pagination,
            func: t.Callable[P, R | t.Coroutine[R, t.Any, t.Any]],
            *,
            signature: inspect.Signature | None = None,
    ) -> t.Callable[P, R | t.Coroutine[R, t.Any, t.Any]]:
        """Apply pagination to a function.

        :param pagination: Pagination techinque to apply.
        :param func: Function to be paginated.
        :param signature: Function signature.
        """
        paginated_handler, schemas = self.PAGINATORS[pagination].wraps(
            func, signature if signature is not None else inspect.signature(func)
        )

        self.schemas.update(schemas)

        return paginated_handler

    def paginated(
            self, pagination: types.Pagination
    ) -> t.Callable[[t.Callable[P, R | t.Coroutine[R, t.Any, t.Any]]], t.Callable[P, R | t.Coroutine[R, t.Any, t.Any]]]:
        def wrapper(func: t.Callable[P, R | t.Coroutine[R, t.Any, t.Any]]):
            return self.apply(pagination, func)

        return wrapper


paginator = Paginator()
