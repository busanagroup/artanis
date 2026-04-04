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
import inspect
import typing as t

from artanis import exceptions
from artanis.asgi import types
from artanis.asgi.modules import Module
from artanis.resources.resource import Resource
from artanis.resources.routing import ResourceRoute

if t.TYPE_CHECKING:
    try:
        from artanis.ddd.repositories.sqlalchemy import SQLAlchemyTableRepository
        from artanis.resources.workers import ResourceWorker
    except exceptions.DependencyNotInstalled:
        ...


__all__ = ["ResourcesModule"]


class ResourcesModule(Module):
    name = "resources"

    def __init__(self, worker: "ResourceWorker | None" = None):
        super().__init__()
        self.worker = worker

    def add_resource(
        self,
        path: str,
        resource: Resource | type[Resource],
        *args,
        include_in_schema: bool = True,
        tags: dict[str, dict[str, t.Any]] | None = None,
        **kwargs,
    ) -> ResourceRoute:
        """Adds a resource to this application, setting its endpoints.

        :param path: Resource base path.
        :param resource: Resource class.
        :param include_in_schema: True if this route or endpoint should be declared as part of the API schema.
        :param tags: Tags to add to the resource.
        """
        if inspect.isclass(resource) and issubclass(resource, Resource):
            resource_instance = resource(*args, **kwargs)
        elif isinstance(resource, Resource):
            resource_instance = resource
        else:
            raise ValueError("Wrong resource")

        route = ResourceRoute(path, resource_instance, parent=self.app, include_in_schema=include_in_schema, tags=tags)
        self.app.mount(mount=route)
        return route

    def resource(
        self,
        path: str,
        *args,
        include_in_schema: bool = True,
        tags: dict[str, dict[str, t.Any]] | None = None,
        **kwargs,
    ) -> t.Callable:
        """Decorator for Resources classes for adding them to the application.

        :param path: Resource base path.
        :param include_in_schema: True if this route or endpoint should be declared as part of the API schema.
        :param tags: Tags to add to the resource.
        :return: Decorated resource class.
        """

        def decorator(resource: type[Resource]) -> type[Resource]:
            self.add_resource(path, resource, *args, include_in_schema=include_in_schema, tags=tags, **kwargs)
            return resource

        return decorator

    def method(
        self,
        path: str,
        *,
        methods: t.Sequence[str] | None = None,
        name: str | None = None,
        include_in_schema: bool = True,
        pagination: types.Pagination | None = None,
        tags: dict[str, t.Any] | None = None,
    ) -> t.Callable:
        """Decorator for adding useful info needed for generating resource routes.

        :param path: Route path.
        :param methods: HTTP methods available.
        :param name: Route name.
        :param include_in_schema: True if this route must be listed as part of the App schema.
        :param pagination: Apply a pagination technique.
        :param tags: Tags to add to the method.
        :return: Decorated method.
        """
        return ResourceRoute.method(
            path, methods=methods, name=name, include_in_schema=include_in_schema, pagination=pagination, tags=tags
        )

    def add_repository(self, name: str, repository: type["SQLAlchemyTableRepository"]) -> None:
        """Register a repository.

        :param name: The name of the repository.
        :param repository: The repository class.
        """
        if self.worker:
            self.worker.add_repository(name, repository)

    def remove_repository(self, name: str) -> None:
        """Deregister a repository.

        :param name: The name of the repository.
        """
        if self.worker:
            self.worker.remove_repository(name)
