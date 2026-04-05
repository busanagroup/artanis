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


import http
from enum import Enum, StrEnum
from typing import Any

import starlette.exceptions

from artanis.helpers import STATUS_CODES


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


class FrameTooLargeError(Exception): ...


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


class InitError(ArtanisException): ...


class ApplicationError(Exception): ...


class DependencyNotInstalled(ApplicationError):
    class Dependency(StrEnum):  # PORT: Replace compat when stop supporting 3.10
        pydantic = "pydantic"
        marshmallow = "marshmallow"
        apispec = "apispec"
        typesystem = "typesystem"
        sqlalchemy = "sqlalchemy[asyncio]"
        httpx = "httpx"
        tomli = "tomli"  # PORT: Remove when stop supporting 3.10

    def __init__(
            self,
            *,
            dependency: str | Dependency | None = None,
            dependant: str | None = None,
            msg: str = "",
    ) -> None:
        super().__init__()
        self.dependency = self.Dependency(dependency) if dependency else None
        self.dependant = dependant
        self.msg = msg

    def __str__(self) -> str:
        if self.dependency:
            s = f"Dependency '{self.dependency.value}' must be installed"
            if self.dependant:
                s += f" to use '{self.dependant}'"
            if self.msg:
                s += f" ({self.msg})"
        else:
            s = self.msg

        return s

    def __repr__(self) -> str:
        params = ("msg", "dependency", "dependant")
        formatted_params = ", ".join([f"{x}={getattr(self, x)}" for x in params if getattr(self, x)])
        return f"{self.__class__.__name__}({formatted_params})"


class SQLAlchemyError(ApplicationError): ...


class DecodeError(Exception):
    """
    Raised by a Codec when `decode` fails due to malformed syntax.
    """

    def __init__(self, message, marker=None, base_format=None) -> None:
        super().__init__(self, message)
        self.message = message
        self.marker = marker
        self.base_format = base_format


class NoCodecAvailable(Exception): ...


class WebSocketException(starlette.exceptions.WebSocketException):
    def __init__(self, code: int, reason: str | None = None) -> None:
        self.code = code
        self.reason = reason or ""

    def __str__(self) -> str:
        return str(self.reason)

    def __repr__(self) -> str:
        params = ("code", "reason")
        formatted_params = ", ".join([f"{x}={getattr(self, x)}" for x in params if getattr(self, x)])
        return f"{self.__class__.__name__}({formatted_params})"

    def __eq__(self, other):
        return isinstance(other, WebSocketException) and self.code == other.code and self.reason == other.reason


class HTTPException(starlette.exceptions.HTTPException):
    def __init__(
            self,
            status_code: int,
            detail: str | dict[str, t.Any] | None = None,
            headers: dict | None = None,
    ) -> None:
        if detail is None:
            detail = http.HTTPStatus(status_code).phrase
        self.status_code = status_code
        self.detail = detail  # type: ignore[assignment]
        self.headers = headers

    def __str__(self) -> str:
        return str(self.detail)

    def __repr__(self) -> str:
        params = ("status_code", "detail", "headers")
        formatted_params = ", ".join([f"{x}={getattr(self, x)}" for x in params if getattr(self, x)])
        return f"{self.__class__.__name__}({formatted_params})"

    def __eq__(self, other):
        return (
                isinstance(other, HTTPException)
                and self.status_code == other.status_code
                and self.detail == other.detail
                and self.headers == other.headers
        )


class ValidationError(HTTPException):
    def __init__(
            self,
            detail: str | dict[str, list[str]] | None = None,
            status_code: int = 400,
    ) -> None:
        super().__init__(status_code, detail=detail)


class SerializationError(HTTPException):
    def __init__(self, detail: None | str | dict[str, list[str]] = None, status_code: int = 500) -> None:
        super().__init__(status_code, detail=detail)


class NotFoundException(Exception):
    def __init__(
            self, path: str | None = None, params: dict[str, t.Any] | None = None, name: str | None = None
    ) -> None:
        self.path = path
        self.params = params
        self.name = name

    def __str__(self) -> str:
        params = ("path", "params", "name")
        formatted_params = ", ".join([f"{x}={repr(getattr(self, x))}" for x in params if getattr(self, x)])
        return f"Path not found ({formatted_params})"

    def __repr__(self) -> str:
        params = ("path", "params", "name")
        formatted_params = ", ".join([f"{x}={repr(getattr(self, x))}" for x in params if getattr(self, x)])
        return f"{self.__class__.__name__}({formatted_params})"


class MethodNotAllowedException(Exception):
    def __init__(self, path: str, method: str, allowed: set[str]) -> None:
        self.path = path
        self.method = method
        self.allowed = allowed

    def __str__(self) -> str:
        params = ("path", "method", "allowed")
        formatted_params = ", ".join([f"{x}={getattr(self, x)}" for x in params if getattr(self, x)])
        return f"Method not allowed ({formatted_params})"

    def __repr__(self) -> str:
        params = ("path", "method", "allowed")
        formatted_params = ", ".join([f"{x}={getattr(self, x)}" for x in params if getattr(self, x)])
        return f"{self.__class__.__name__}({formatted_params})"


class FrameworkNotInstalled(Exception):
    """Cannot find an installed version of the framework."""
    ...


class FrameworkVersionWarning(Warning):
    """Warning for when a framework version does not match."""
    ...
