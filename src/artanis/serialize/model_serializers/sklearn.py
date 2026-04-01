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
import logging
import math
import pickle
import typing as t
import warnings

from artanis.asgi import types
from artanis import exceptions
from artanis.serialize.model_serializers.base import BaseModelSerializer

if t.TYPE_CHECKING:
    from artanis.asgi.types import JSONField, JSONSchema

logger = logging.getLogger(__name__)


__all__ = ["ModelSerializer"]


class ModelSerializer(BaseModelSerializer):
    lib: t.ClassVar[types.MLLib] = "sklearn"

    def dump(self, obj: t.Any, /, **kwargs) -> bytes:
        return codecs.encode(pickle.dumps(obj), "base64")

    def load(self, model: bytes, /, **kwargs) -> t.Any:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = pickle.loads(codecs.decode(model, "base64"))

        return model

    def _info(self, data, /) -> "JSONField":
        if isinstance(data, int | bool | str):
            return data

        if isinstance(data, float):
            return None if math.isnan(data) else data

        if isinstance(data, dict):
            return {k: self._info(v) for k, v in data.items()}

        if isinstance(data, list | tuple | set):
            return [self._info(i) for i in data]

        return None

    def info(self, model: t.Any) -> "JSONSchema | None":
        try:
            return self._info(model.get_params())  # type: ignore
        except:  # noqa
            logger.exception("Cannot collect info from model")
            return None

    def version(self) -> str:
        try:
            return importlib.metadata.version("scikit-learn")
        except Exception:  # noqa
            raise exceptions.FrameworkNotInstalled("scikit-learn")
