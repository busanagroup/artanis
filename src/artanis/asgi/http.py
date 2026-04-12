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
import dataclasses
import datetime
import enum
import html
import importlib.util
import inspect
import json
import os
import pathlib
import typing as t
import uuid
import warnings

import jinja2
import starlette.requests
import starlette.responses
import starlette.schemas
import starlette.types
import starlette.exceptions

from artanis import exceptions

__all__ = [
    "Method",
    "Request",
    "Response",
    "HTMLResponse",
    "PlainTextResponse",
    "JSONResponse",
    "RedirectResponse",
    "StreamingResponse",
    "FileResponse",
    "APIErrorResponse",
    "HTMLFileResponse",
    "HTMLTemplatesEnvironment",
    "HTMLTemplateResponse",
]

Method = enum.StrEnum(
    "Method",
    ["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"],
)
Request = starlette.requests.Request


class Response(starlette.responses.Response):
    async def __call__(  # type: ignore[override]
            self, scope: starlette.types.Scope, receive: starlette.types.Receive, send: starlette.types.Send
    ) -> None:
        await super().__call__(scope, receive, send)  # type: ignore[arg-type]

    def __hash__(self) -> int:
        return hash(
            (
                self.status_code,
                getattr(self, "media_type"),
                self.background,
                self.body,
                self.headers,
            )
        )

    def __eq__(self, value: object, /) -> bool:
        return (
                isinstance(value, Response)
                and self.status_code == value.status_code
                and getattr(self, "media_type") == getattr(value, "media_type")
                and self.background == value.background
                and self.body == value.body
                and self.headers == value.headers
        )


class HTMLResponse(starlette.responses.HTMLResponse, Response):
    async def __call__(  # type: ignore[override]
            self, scope: starlette.types.Scope, receive: starlette.types.Receive, send: starlette.types.Send
    ) -> None:
        await super().__call__(scope, receive, send)  # type: ignore[arg-type]


class PlainTextResponse(starlette.responses.PlainTextResponse, Response):
    async def __call__(  # type: ignore[override]
            self, scope: starlette.types.Scope, receive: starlette.types.Receive, send: starlette.types.Send
    ) -> None:
        await super().__call__(scope, receive, send)  # type: ignore[arg-type]


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, pathlib.Path | os.PathLike | uuid.UUID):
            return str(o)
        if isinstance(o, bytes | bytearray):
            return o.decode("utf-8")
        if isinstance(o, enum.Enum):
            return o.value
        if isinstance(o, set | frozenset):
            return list(o)
        if isinstance(o, datetime.datetime | datetime.date | datetime.time):
            return o.isoformat()
        if isinstance(o, datetime.timedelta):
            # split seconds to larger units
            seconds = o.total_seconds()
            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)
            days, hours, minutes = map(int, (days, hours, minutes))
            seconds = round(seconds, 6)

            formatted_units = (
                (days, f"{days:02d}".lstrip("0") + "D"),
                (hours, f"{hours:02d}".lstrip("0") + "H"),
                (minutes, f"{minutes:02d}".lstrip("0") + "M"),
                (seconds, f"{seconds:.6f}".strip("0") + "S"),
            )

            return "P" + "".join([formatted_value for value, formatted_value in formatted_units if value])
        if inspect.isclass(o) and issubclass(o, BaseException):
            return o.__name__
        if isinstance(o, BaseException):
            return repr(o)
        if dataclasses.is_dataclass(o) and not isinstance(o, type):
            return dataclasses.asdict(o)
        return super().default(o)


class JSONResponse(starlette.responses.JSONResponse, Response):
    async def __call__(  # type: ignore[override]
            self, scope: starlette.types.Scope, receive: starlette.types.Receive, send: starlette.types.Send
    ) -> None:
        await super().__call__(scope, receive, send)  # type: ignore[arg-type]

    def render(self, content: t.Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=EnhancedJSONEncoder,
        ).encode("utf-8")


class RedirectResponse(starlette.responses.RedirectResponse, Response):
    async def __call__(  # type: ignore[override]
            self, scope: starlette.types.Scope, receive: starlette.types.Receive, send: starlette.types.Send
    ) -> None:
        await super().__call__(scope, receive, send)  # type: ignore[arg-type]


class StreamingResponse(starlette.responses.StreamingResponse, Response):
    async def __call__(  # type: ignore[override]
            self, scope: starlette.types.Scope, receive: starlette.types.Receive, send: starlette.types.Send
    ) -> None:
        await super().__call__(scope, receive, send)  # type: ignore[arg-type]


class FileResponse(starlette.responses.FileResponse, Response):
    async def __call__(  # type: ignore[override]
            self, scope: starlette.types.Scope, receive: starlette.types.Receive, send: starlette.types.Send
    ) -> None:
        await super().__call__(scope, receive, send)  # type: ignore[arg-type]


class HTMLFileResponse(HTMLResponse):
    def __init__(self, path: str, *args, **kwargs):
        try:
            with open(path) as f:
                content = f.read()
        except Exception as e:
            raise starlette.exceptions.HTTPException(status_code=500, detail=str(e))

        super().__init__(content, *args, **kwargs)


class HTMLTemplatesEnvironment(jinja2.Environment):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **{
                **kwargs,
                "comment_start_string": "||*",
                "comment_end_string": "*||",
                "block_start_string": "||%",
                "block_end_string": "%||",
                "variable_start_string": "||@",
                "variable_end_string": "@||",
            },
        )

        self.filters["safe"] = self.safe
        self.filters["safe_json"] = self.safe_json

    @t.overload
    def _escape(self, value: str) -> str:
        ...

    @t.overload
    def _escape(self, value: bool) -> bool:
        ...

    @t.overload
    def _escape(self, value: int) -> int:
        ...

    @t.overload
    def _escape(self, value: float) -> float:
        ...

    @t.overload
    def _escape(self, value: None) -> None:
        ...

    def _escape(self, value: t.Any) -> t.Any:
        if isinstance(value, list | tuple):
            return [self._escape(x) for x in value]

        if isinstance(value, dict):
            return {k: self._escape(v) for k, v in value.items()}

        if isinstance(value, str):
            return html.escape(value).replace("\n", "&#10;&#13;")

        return value

    def safe(self, value: str) -> str:
        return self._escape(value)

    def safe_json(self, value: t.Any):
        return json.dumps(self._escape(value), cls=EnhancedJSONEncoder).replace('"', '\\"')


class HTMLTemplateResponse(HTMLResponse):
    templates = HTMLTemplatesEnvironment(loader=jinja2.FileSystemLoader(pathlib.Path(os.curdir) / "templates"))

    def __init__(self, template: str, context: dict[str, t.Any] | None = None, *args, **kwargs):
        if context is None:
            context = {}

        super().__init__(self.templates.get_template(template).render(**context), *args, **kwargs)


class _ArtanisLoader(jinja2.PackageLoader):
    def __init__(self):
        spec = importlib.util.find_spec("artanis")
        if spec is None or spec.origin is None:
            raise exceptions.ArtanisError("Artanis package not found")

        templates_path = pathlib.Path(spec.origin).parent.joinpath("asgi", "openapi", "templates")
        if not templates_path.exists():
            warnings.warn("Templates folder not found in the Artanis package")
            templates_path.mkdir(exist_ok=True)

        super().__init__(package_name="artanis.asgi.openapi", package_path="templates")


class ArtanisTemplateResponse(HTMLTemplateResponse):
    templates = HTMLTemplatesEnvironment(loader=_ArtanisLoader())

