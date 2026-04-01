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
# This module is part of Artanis Enterprise Platform and is released under
# the Apache-2.0 License: https://www.apache.org/licenses/LICENSE-2.0
class ResourceAttributeError(AttributeError):
    ATTRIBUTE_NOT_FOUND = "needs to define attribute '{attribute}'"
    # RESTResource
    SCHEMA_NOT_FOUND = "needs to define attribute 'schema' or the pair 'input_schema' and 'output_schema'"
    RESOURCE_NAME_INVALID = "invalid resource name '{resource_name}'"
    PK_NOT_FOUND = "model must define a single-column primary key"
    PK_WRONG_TYPE = "model primary key wrong type"
    MODEL_INVALID = "model must be a valid SQLAlchemy Table instance or a Model instance"
    # ModelResource
    MODEL_NOT_FOUND = "needs to define attribute 'model_path' or 'component'"

    def __init__(self, msg: str, name: str):
        super().__init__(f"{name} {msg}")
