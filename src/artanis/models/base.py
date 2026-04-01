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
import abc
import typing as t

if t.TYPE_CHECKING:
    from artanis.serialize.data_structures import Artifacts, Metadata

__all__ = ["BaseModel"]


class BaseModel:
    def __init__(self, model: t.Any, meta: "Metadata", artifacts: "Artifacts | None"):
        self.model = model
        self.meta = meta
        self.artifacts = artifacts

    def inspect(self) -> t.Any:
        return {"meta": self.meta.to_dict(), "artifacts": self.artifacts}

    @abc.abstractmethod
    def predict(self, x: t.Any) -> t.Any: ...
