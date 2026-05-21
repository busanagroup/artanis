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
import json
from lxml import etree
import xmltodict


class XMLImport:
    identifier: str = "artanis"

    def parse(self, root: etree._Element, dest: pathlib.Path):
        """
        Parses an XML Element, validates it against a RelaxNG schema, and converts it to a JSON file.

        Args:
            root (lxml.etree._Element): The root XML element to parse and validate.
                                        It is assumed to be an lxml element for schema validation.
            dest (pathlib.Path): The path to the output JSON file.
        """
        assert root.tag == self.identifier, f"Root XML tag must be <{self.identifier}>, but got <{root.tag}>."

        # Determine the path to the schema.rng file.
        # Assuming schema.rng is located in the same directory as this xmlimport.py file.
        schema_path = pathlib.Path(__file__).parent / "schema.rng"

        if not schema_path.exists():
            raise FileNotFoundError(f"RelaxNG schema file not found at '{schema_path}'.")

        # Load the RelaxNG schema for validation
        try:
            relaxng = etree.RelaxNG(file=str(schema_path))
        except etree.XMLSyntaxError as e:
            raise ValueError(f"Failed to parse RelaxNG schema from '{schema_path}': {e}")

        # Validate the XML document against the loaded schema
        try:
            relaxng.assertValid(root)
        except etree.DocumentInvalid as e:
            raise ValueError(f"XML document validation failed against schema '{schema_path}': {e}")

        # Convert the lxml element back to a string, then parse it with xmltodict.
        # pretty_print is used for readability of the intermediate XML string,
        # though xmltodict can parse non-pretty-printed XML just fine.
        xml_string = etree.tostring(root, pretty_print=True, encoding='utf-8').decode('utf-8')

        # Convert the XML string to a Python dictionary using xmltodict.
        # xmltodict.parse typically returns an OrderedDict, which is compatible with json.dump.
        xml_dict = xmltodict.parse(xml_string)

        # Write the resulting dictionary to the destination JSON file.
        # indent=4 is used for pretty-printing the JSON output.
        with open(dest, 'w', encoding='utf-8') as f:
            json.dump(xml_dict, f, indent=4)
