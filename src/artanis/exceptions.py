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

from artanis.helpers import STATUS_CODES
from enum import Enum
from typing import Any


class ShutdownError(Exception):
    pass


class NoAppError(Exception):
    pass


class ConfigError(Exception):
    """ Exception raised on config error """


class LifespanTimeoutError(Exception):
    def __init__(self, stage: str) -> None:
        super().__init__(
            f"Timeout whilst awaiting {stage}. Your application may not support the ASGI Lifespan "
            f"protocol correctly, alternatively the {stage}_timeout configuration is incorrect."
        )


class LifespanFailureError(Exception):
    def __init__(self, stage: str, message: str) -> None:
        super().__init__(f"Lifespan failure in {stage}. '{message}'")


class UnexpectedMessageError(Exception):
    def __init__(self, state: Enum, message_type: str) -> None:
        super().__init__(f"Unexpected message type, {message_type} given the state {state}")


class FrameTooLargeError(Exception):
    pass


class ArtanisError(RuntimeError):
    """
    A generic, Artanis error.
    """


class ArtanisException(Exception):
    """Generic exception that will generate an HTTP response when raised in the context of a request lifecycle.

    Usually, it is best practice to use one of the more specific exceptions
    than this generic one. Even when trying to raise a 500, it is generally
    preferable to use `ServerError`.

    Args:
        message (Optional[Union[str, bytes]], optional): The message to be sent to the client. If `None`,
            then the appropriate HTTP response status message will be used instead. Defaults to `None`.
        status_code (Optional[int], optional): The HTTP response code to send, if applicable. If `None`,
            then it will be 500. Defaults to `None`.
        quiet (Optional[bool], optional): When `True`, the error traceback will be suppressed from the logs.
            Defaults to `None`.
        context (Optional[Dict[str, Any]], optional): Additional mapping of key/value data that will be
            sent to the client upon exception. Defaults to `None`.
        extra (Optional[Dict[str, Any]], optional): Additional mapping of key/value data that will NOT be
            sent to the client when in PRODUCTION mode. Defaults to `None`.
        headers (Optional[Dict[str, Any]], optional): Additional headers that should be sent with the HTTP
            response. Defaults to `None`.

    Examples:
        ```python
        raise ArtanisException(
            "Something went wrong",
            status_code=999,
            context={
                "info": "Some additional details to send to the client",
            },
            headers={
                "X-Foo": "bar"
            }
        )
        ```
    """  # noqa: E501

    status_code: int = 500
    quiet: bool | None = False
    headers: dict[str, str] = {}
    message: str = ""

    def __init__(
            self,
            message: str | bytes | None = None,
            status_code: int | None = None,
            *,
            quiet: bool | None = None,
            context: dict[str, Any] | None = None,
            extra: dict[str, Any] | None = None,
            headers: dict[str, str] | None = None,
    ) -> None:
        self.context = context
        self.extra = extra
        status_code = status_code or getattr(
            self.__class__, "status_code", None
        )
        quiet = (
            quiet
            if quiet is not None
            else getattr(self.__class__, "quiet", None)
        )
        headers = headers or getattr(self.__class__, "headers", {})
        if message is None:
            message = self.message
            if not message and status_code:
                msg = STATUS_CODES.get(status_code, b"")
                message = msg.decode()
        elif isinstance(message, bytes):
            message = message.decode()

        super().__init__(message)

        self.status_code = status_code or self.status_code
        self.quiet = quiet
        self.headers = headers
        try:
            self.message = message
        except AttributeError:
            ...


class ValidationError(ArtanisException):
    status_code = 400


class InitError(ArtanisException): ...
