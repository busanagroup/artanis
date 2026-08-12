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

import glob
import importlib.util
import logging
import os.path
import pathlib
from os.path import basename, isfile, dirname
from pprint import pprint

from lxml import etree, builder

from artanis import exceptions
from artanis.config import Configuration
from artanis.defs.xmlimport import XMLImport

logger = logging.getLogger(__name__)

async def convert_xml(source: pathlib.Path, dest: pathlib.Path) -> None:
    logger.info(f"converting: ... {str(basename(source))}")
    relaxng = None
    try:
        doc = etree.parse(source)
        schema = os.path.join(dirname(__file__), 'schema.rng')
        relax_tree = etree.parse(schema)
        relaxng = etree.RelaxNG(relax_tree)
        relaxng.assert_(doc)
    except Exception:
        logger.exception("The XML file '%s' does not fit the required schema!", source.name)
        if relaxng:
            for e in relaxng.error_log:
                logger.warning(e)
        raise
    obj = XMLImport(relax_tree)
    obj.parse(doc.getroot(), dest)
    action_menu = dict()
    view_def = dict()
    if '__default_menu__' in obj.menu_definition:
        action_menu['menu_definition'] = obj.menu_definition
    if obj.action_view:
        action_menu['action_view'] = obj.action_view
    if len(obj.view_def) > 0:
        view_def["views"] = obj.view_def
    if len(obj.search_filters) > 0:
        view_def["search_filters"] = obj.search_filters
    if len(obj.actions) > 0:
        view_def["actions"] = obj.actions
    with open(dest, "w+") as file:
        if len(view_def) > 0:
            pprint(view_def, stream=file, indent=1)
        if action_menu:
            pprint(action_menu, stream=file, indent=1)



def ensure_exist(path: pathlib.Path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

async def load_xml(config: Configuration):
    spec = importlib.util.find_spec("ecf")
    if spec is None or spec.origin is None:
        raise exceptions.ApplicationError("ECF package not found")

    resource_path = pathlib.Path(spec.origin).parent.joinpath("res", "xml")
    json_path = pathlib.Path(spec.origin).parent.joinpath("res")
    ensure_exist(resource_path)
    ensure_exist(json_path)
    resource_files = resource_path / "*.xml"
    for f in glob.glob(str(resource_files)):
        if isfile(f):
            dest_file = json_path / f"{os.path.splitext(basename(f))[0]}.py"
            await convert_xml(pathlib.Path(f), dest_file)

