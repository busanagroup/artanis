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
from __future__ import annotations

import ast
import importlib.util
import pathlib

from lru import LRU as LRUDict

from artanis import exceptions


class BaseDefinition:

    __base_path__: pathlib.Path

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        spec = importlib.util.find_spec("ecf")
        cls.__base_path__ = pathlib.Path(spec.origin).parent.joinpath("res")

class MenuDefinition(BaseDefinition):


    def __init__(self):
        self.__definition__: dict

        path = self.__base_path__.joinpath("__menu__.py")
        if not path.is_file():
            raise exceptions.DefinitionNotFoundError(f"Menu definition file not found: {str(path)}")
        with open(path, "r+") as file:
            self.__definition__ = ast.literal_eval(file.read())

    @property
    def definition(self) -> dict:
        return self.__definition__

    def get_menu_definition(self, definition: str):
        menu =  self.definition['menu_definition']
        definition = definition if definition in menu else '__default_menu__'
        return menu[definition]

    def get_action_view(self, definition: str):
        action_view = self.definition['action_view']
        view: dict = action_view.get(definition)
        if not view:
            return None
        viewdef = {key: view[key] for key in ['service', 'title', 'type'] if key in view}
        if 'type' not in viewdef.keys():
            viewdef['type'] = 'grid'
        for item in view['views']:
            if item['defkind'] == 'view-param':
                viewdef['params'] = {item['name']: item['value']}
                break
        viewdef['views'] = [item for item in view['views'] if item['defkind'] != 'view-param']
        return viewdef


class ViewDefinition(BaseDefinition):
    __instances = LRUDict(size=16)

    def get_definition(self, service_name: str) -> dict:
        definition: dict = ViewDefinition.__instances.get(service_name)
        if not definition:
            path = self.__base_path__.joinpath(f"{service_name}.py")
            if not path.is_file():
                raise exceptions.DefinitionNotFoundError(f"View definition file not found: {str(path)}")
            with open(path, "r+") as file:
                definition = ast.literal_eval(file.read())
                ViewDefinition.__instances[service_name] = definition
        return definition

    def get_viewdef(self, service_name: str, view: str):
        definition: dict = self.get_definition(service_name)
        views = definition.get('views', {})
        return views.get(view)

    def get_search_filter(self, service_name: str, filter: str):
        definition: dict = self.get_definition(service_name)
        filters = definition.get('search_filters', {})
        return filters.get(filter)

    def get_action(self, service_name: str, action: str):
        definition: dict = self.get_definition(service_name)
        actions = definition.get('actions', {})
        return actions.get(action)
