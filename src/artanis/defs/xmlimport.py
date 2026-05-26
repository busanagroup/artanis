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
import pathlib
from xml.etree.ElementTree import ParseError

from lxml import etree


class XMLImport:
    identifier: str = "artanis"

    CAST_MAP = {
        "boolean": lambda v: v.strip().lower() in ("true", "1", "yes"),
        "int": int,
        "integer": int,
        "decimal": float,
        "string": str,
    }

    def __init__(self, relax_tree):
        self.initialized: bool = False
        self.relaxng_tree = relax_tree
        self.menu_definition: dict = dict()
        self.action_view = dict()
        self.registry = dict()
        self._tags = {
            'menu': self.tag_menu,
            'action-view': self.tag_action_view,
            'grid': self.tag_grid,
            'form': self.tag_form,
            'search-filters': self.tag_search_filters,
            'action-menu': self.tag_action_menu,
            'action-validate': self.tag_action_validate,
            'action-condition': self.tag_action_condition,
            'action-record': self.tag_action_record,
            'action-attrs': self.tag_action_attrs,
            'action-method': self.tag_action_method,
            'action-script': self.tag_action_script,
            'action-ws': self.tag_action_ws,
            'action-import': self.tag_action_import,
            'action-export': self.tag_action_export,
            'action-group': self.tag_action_group,
            'action-report': self.tag_action_report,
        }

    def init_registry(self):
        if self.initialized:
            return None
        ns = {'rng': 'http://relaxng.org/ns/structure/1.0'}
        attributes = self.relaxng_tree.xpath("//rng:attribute", namespaces=ns)
        try:
            for attr in attributes:
                name = attr.get("name")
                # Look for the data type inside the attribute
                data_tag = attr.find(".//rng:data", namespaces=ns)

                if name and data_tag is not None:
                    rng_type = data_tag.get("type")
                    if rng_type in self.CAST_MAP:
                        self.registry[name] = self.CAST_MAP[rng_type]
        finally:
            self.initialized = True
        return self.registry



    def parse(self, root: etree._Element, dest: pathlib.Path):
        """
        Parses an XML Element, validates it against a RelaxNG schema, and converts it to a JSON file.

        Args:
            root (lxml.etree._Element): The root XML element to parse and validate.
                                        It is assumed to be an lxml element for schema validation.
            dest (pathlib.Path): The path to the output JSON file.
        """
        self.init_registry()
        assert root.tag == self.identifier, f"Root XML tag must be <{self.identifier}>, but got <{root.tag}>."

        self.tag_root(root)

    def tag_root(self, element):
        for rec in element:
            func = self._tags.get(rec.tag)
            if func is None:
                continue
            try:
                func(rec)
            except ParseError:
                raise

    def convert_dict(self, attrib, **kwargs):
        def convert_val(key, val):
            try:
                return self.registry[key](val) if key in self.registry else val
            except (ValueError, TypeError):
                return val
        return dict([(key, convert_val(key, val)) for key, val in attrib.items()], **kwargs)


    def tag_menu_item(self, element, parent) -> list:
        el_list = [self.convert_dict(element.attrib)] if parent is None else [self.convert_dict(element.attrib, parent=parent.get("name"))]
        for rec in element:
            if element.tag == "item":
                el_list += self.tag_menu_item(rec, element)
        return el_list

    def tag_menu(self, element):
        is_root = element.tag == "menu"
        assert is_root, "Identifier must be a 'menu'"
        el_list = []
        for rec in element:
            if rec.tag == "item":
                el_list += self.tag_menu_item(rec, None)
        self.menu_definition[element.get("name")] = el_list

    def tag_action_view(self, element):
        is_root = element.tag == "action-view"
        assert is_root, "Identifier must be a 'action-view'"
        for rec in element:
            if rec.tag == "action":
                self.action_view[rec.get("name")] = self.convert_dict(rec.attrib, views=[self.convert_dict(view.attrib) for view in rec])

    def tag_grid(self, element):
        ...

    def tag_form(self, element):
        ...

    def tag_search_filters(self, element):
        ...

    def tag_action_menu(self, element):
        ...

    def tag_action_validate(self, element):
        ...

    def tag_action_condition(self, element):
        ...

    def tag_action_record(self, element):
        ...

    def tag_action_attrs(self, element):
        ...

    def tag_action_method(self, element):
        ...

    def tag_action_script(self, element):
        ...

    def tag_action_ws(self, element):
        ...

    def tag_action_import(self, element):
        ...

    def tag_action_export(self, element):
        ...

    def tag_action_group(self, element):
        ...

    def tag_action_report(self, element):
        ...
