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

from __future__ import annotations

__all__ = ['WorkerFactory', ]

import weakref
from abc import ABC, abstractmethod
from multiprocessing.context import BaseContext
from multiprocessing.synchronize import Event as EventType

from artanis.abc.configurable import Configurable
from artanis.abc.singleton import Singleton


class WorkerFactory(Configurable, Singleton, ABC):
    worker_name: str

    def __init__(self, parent):
        self.parent = weakref.ref(parent)
        config = parent.get_configuration()
        super().__init__(config=config)

    def get_worker_name(self) -> str:
        return self.worker_name

    def get_parent(self):
        return self.parent()

    def get_process_count(self):
        parent = self.get_parent()
        return parent.get_process_count()

    def get_processes(self, processes: list):
        return len([a for a, b in processes if b == self.worker_name])

    @abstractmethod
    def create_worker(self, processes: list, ctx: BaseContext, shutdown_event: EventType):
        ...
