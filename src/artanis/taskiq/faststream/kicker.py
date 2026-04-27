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

from typing import Any

from taskiq.kicker import AsyncKicker, _FuncParams, _ReturnType
from taskiq.message import TaskiqMessage


class LabelRespectKicker(AsyncKicker[_FuncParams, _ReturnType]):
    """Patched kicker doesn't cast labels to str."""

    def _prepare_message(self, *args: Any, **kwargs: Any) -> TaskiqMessage:
        msg = super()._prepare_message(*args, **kwargs)
        msg.labels = self.labels
        return msg
