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
import typing as t

from artanis import exceptions
from artanis.models.base import BaseModel

try:
    import torch  # type: ignore
except Exception:  # pragma: no cover
    torch = None  # type: ignore

__all__ = ["Model"]


class Model(BaseModel):
    def predict(self, x: list[list[t.Any]]) -> t.Any:
        if torch is None:  # noqa
            raise exceptions.FrameworkNotInstalled("pytorch")

        try:
            return self.model(torch.Tensor(x)).tolist()
        except ValueError as e:
            raise exceptions.HTTPException(status_code=400, detail=str(e))
