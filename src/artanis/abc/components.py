#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2025 Busana Apparel Group. All rights reserved.
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

from artanis.asgi import types
from artanis.abc.workers import AbstractWorker
from artanis.injection import Component

if t.TYPE_CHECKING:
    from artanis.injection import Parameter


__all__ = ["WorkerComponent"]


class WorkerComponent(Component):
    def __init__(self, worker: AbstractWorker):
        self.worker = worker

    def can_handle_parameter(self, parameter: "Parameter") -> bool:
        return parameter.annotation is self.worker.__class__

    def resolve(self, scope: types.Scope):
        self.worker.app = scope["root_app"]
        return self.worker
