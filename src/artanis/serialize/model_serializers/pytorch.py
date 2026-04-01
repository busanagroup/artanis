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
import codecs
import importlib.metadata
import io
import typing as t

from artanis.asgi import types
from artanis import exceptions
from artanis.serialize.model_serializers.base import BaseModelSerializer

try:
    import torch  # type: ignore
except Exception:  # pragma: no cover
    torch = None  # type: ignore[misc, assignment]

if t.TYPE_CHECKING:
    from artanis.asgi.types import JSONSchema

__all__ = ["ModelSerializer"]


class ModelSerializer(BaseModelSerializer):
    lib: t.ClassVar[types.MLLib] = "torch"

    def dump(self, obj: t.Any, /, **kwargs) -> bytes:
        if torch is None:  # noqa
            raise exceptions.FrameworkNotInstalled("pytorch")

        buffer = io.BytesIO()
        torch.jit.save(torch.jit.script(obj), buffer, **kwargs)
        buffer.seek(0)
        return codecs.encode(buffer.read(), "base64")

    def load(self, model: bytes, /, **kwargs) -> t.Any:
        if torch is None:  # noqa
            raise exceptions.FrameworkNotInstalled("pytorch")

        return torch.jit.load(io.BytesIO(codecs.decode(model, "base64")), **kwargs)

    def info(self, model: t.Any, /) -> "JSONSchema | None":
        return {
            "modules": [str(x) for x in model.modules()],
            "parameters": {k: str(v) for k, v in model.named_parameters()},
            "state": {k: v.tolist() if hasattr(v, "tolist") else v for k, v in model.state_dict().items()},
        }

    def version(self) -> str:
        try:
            return importlib.metadata.version("torch")
        except Exception:  # noqa
            raise exceptions.FrameworkNotInstalled("pytorch")
