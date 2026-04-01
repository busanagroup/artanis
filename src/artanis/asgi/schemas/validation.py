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
import inspect
from functools import wraps

from artanis import exceptions
from artanis.asgi.schemas.data_structures import Schema
from artanis.asgi.schemas.exceptions import SchemaValidationError

__all__ = ["output_validation"]


def output_validation(error_cls=exceptions.ValidationError, error_status_code=500):
    """
    Validate view output using schema annotated as function's return.

    :param error_cls: Error class to be raised when validation fails. Errors dict will be passed through 'detail' param.
    :param error_status_code: HTTP status code assigned to response when it fails to validate output, default 500.
    :raises exceptions.ValidationError: if output validation fails.
    """

    def outer_decorator(func):
        try:
            schema = Schema.from_type(inspect.signature(func).return_annotation)
        except Exception as e:
            raise TypeError(f"Invalid return signature for function '{func}'") from e

        @wraps(func)
        async def inner_decorator(*args, **kwargs):
            response = await func(*args, **kwargs) if inspect.iscoroutinefunction(func) else func(*args, **kwargs)

            try:
                # Use output schema to validate the data
                schema.validate(schema.dump(response))
            except SchemaValidationError as e:
                raise error_cls(detail=e.errors, status_code=error_status_code)
            except Exception as e:
                raise error_cls(
                    detail=f"Error serializing response before validation: {str(e)}", status_code=error_status_code
                )

            return response

        return inner_decorator

    return outer_decorator
