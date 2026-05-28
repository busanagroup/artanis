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



