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

from artanis import injection
from artanis.abc.objloader import ObjectLoader
from artanis.abc.objlock import SyncLock
from artanis.abc.service import StartableService
from artanis.abc.singleton import Singleton
from artanis.asgi.schemas.modules import SchemaModule
from artanis.ddd import WorkerComponent
from artanis.injection import injector, Components
from artanis.models import ModelsModule
from artanis.modules import Modules
from artanis.resources import ResourcesModule
from artanis.resources.workers import ResourceWorker


class BaseBrokerService(StartableService, Singleton, SyncLock, ObjectLoader):
    resources: ResourcesModule
    schema: SchemaModule
    models: ModelsModule

    def __init__(
            self,
            *args,
            debug: bool = False,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.debug = debug
        self._injector = injector.Injector(Context)

        default_components = []

        if (worker := ResourceWorker() if ResourceWorker else None) and WorkerComponent:
            default_components.append(WorkerComponent(worker=worker))

        default_modules = [
            ResourcesModule(worker=worker),
            SchemaModule(None),
            ModelsModule(),
        ]
        self.modules = Modules(app=self, modules={*default_modules, *([])})
        self._components =  Components([*default_modules])
        self.schema.schema_library = 'pydantic'

    def __getattr__(self, item: str) -> t.Any:
        try:
            return self.modules.__getitem__(item)
        except KeyError:
            return None

    @property
    def components(self) -> injection.Components:
        return Components(self._components + (self.parent.components if self.parent else ()))

    @property
    def injector(self) -> injection.Injector:
        components = injection.Components(self.components + asgi.ASGI_COMPONENTS + validation.VALIDATION_COMPONENTS)
        if self._injector.components != components:
            self._injector.components = components
        return self._injector


class Context(injection.Context):
    types = {
        "exc": Exception,
        "app": BaseBrokerService,
    }

    hashable = (
        "exc",
        "app",
    )
