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
import os
import typing as t

from artanis.models.resource import ModelResource, ModelResourceType
from artanis.modules import Module

if t.TYPE_CHECKING:
    from artanis.resources import ResourceRoute

__all__ = ["ModelsModule"]


class ModelsModule(Module):
    name = "models"

    def add_model(
        self,
        path: str,
        model: str | os.PathLike,
        name: str,
        tags: dict[str, dict[str, t.Any]] | None = None,
        *args,
        **kwargs,
    ) -> "ResourceRoute":
        """Adds a model to this application, setting its endpoints.

        :param path: Resource base path.
        :param model: Model path.
        :param name: Model name.
        :param tags: Tags to add to the model methods.
        """

        name_ = name
        model_ = model

        class Resource(ModelResource, metaclass=ModelResourceType):
            name = name_
            model_path = model_

        resource = Resource()
        self.app.add_component(resource.component)
        return self.app.resources.add_resource(path, resource, tags=tags, *args, **kwargs)

    def model_resource(self, path: str, tags: dict[str, dict[str, t.Any]] | None = None, *args, **kwargs) -> t.Callable:
        """Decorator for ModelResource classes for adding them to the application.

        :param path: Resource base path.
        :param tags: Tags to add to the model methods.
        :return: Decorated resource class.
        """

        def decorator(resource: type[ModelResource]) -> type[ModelResource]:
            self.app.models.add_model_resource(path, resource, tags=tags, *args, **kwargs)
            return resource

        return decorator

    def add_model_resource(
        self,
        path: str,
        resource: ModelResource | type[ModelResource],
        tags: dict[str, dict[str, t.Any]] | None = None,
        *args,
        **kwargs,
    ) -> "ResourceRoute":
        """Adds a resource to this application, setting its endpoints.

        :param path: Resource base path.
        :param resource: Resource class.
        :param tags: Tags to add to the model methods.
        """
        self.app.add_component(resource.component)
        return self.app.resources.add_resource(path, resource, tags=tags, *args, **kwargs)
