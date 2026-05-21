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
        relaxng = etree.RelaxNG(etree.parse(schema))
        relaxng.assert_(doc)
    except Exception:
        logger.exception("The XML file '%s' does not fit the required schema!", source.name)
        if relaxng:
            for e in relaxng.error_log:
                logger.warning(e)
        raise

    obj = XMLImport()
    obj.parse(doc.getroot(), dest)

def ensure_exist(path: pathlib.Path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

async def load_xml(config: Configuration):
    spec = importlib.util.find_spec("ecf")
    if spec is None or spec.origin is None:
        raise exceptions.ApplicationError("ECF package not found")

    resource_path = pathlib.Path(spec.origin).parent.joinpath("res", "xml")
    json_path = pathlib.Path(spec.origin).parent.joinpath("res", "json")
    ensure_exist(resource_path)
    ensure_exist(json_path)
    resource_files = resource_path / "*.xml"
    for f in glob.glob(str(resource_files)):
        if isfile(f):
            dest_file = json_path / f"{os.path.splitext(basename(f))[0]}.json"
            await convert_xml(pathlib.Path(f), dest_file)

