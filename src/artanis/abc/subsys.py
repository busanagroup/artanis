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
# This module is part of Centric PLM Integration Bridge and is released under
# the Apache-2.0 License: https://www.apache.org/licenses/LICENSE-2.0
from __future__ import annotations

from typing import Type

from .singleton import Singleton
from .startable import Startable
from .objlock import SyncLock
from .factory import WorkerFactory


class Subsystem(Startable, Singleton, SyncLock):
    process_count: int = 0
    factory: WorkerFactory = None
    class_factory: Type[WorkerFactory]
    config_service_enabled: str
    subsystem_name: str

    def __init__(self, config=None):
        super().__init__(config=config)

    def get_process_count(self):
        return self.process_count

    def get_factory(self):
        if not self.factory:
            self.factory = self.class_factory(self)
        return self.factory

    @classmethod
    def subsystem_enabled(cls, config) -> bool:
        return config.get_property_value(cls.config_service_enabled, "false").lower() == "true"
