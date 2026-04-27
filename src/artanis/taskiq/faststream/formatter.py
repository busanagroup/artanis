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

from dataclasses import dataclass
from typing import Any

from taskiq.abc.formatter import TaskiqFormatter
from taskiq.message import TaskiqMessage


@dataclass
class PatchedMessage:
    """DTO to transfer data to `broker.kick`."""

    body: Any
    labels: dict[str, Any]


class PatchedFormatter(TaskiqFormatter):
    """Default taskiq formatter."""

    def dumps(  # type: ignore[override]
            self,
            message: TaskiqMessage,
    ) -> PatchedMessage:
        """
        Dumps taskiq message to some broker message format.

        :param message: message to send.
        :return: Dumped message.
        """
        labels = message.labels.copy()
        labels.pop("schedule", None)
        labels.pop("schedule_id", None)

        return PatchedMessage(
            body=labels.pop("message", None),
            labels=labels,
        )

    def loads(self, message: bytes) -> TaskiqMessage:
        """
        Loads json from message.

        :param message: broker's message.
        :return: parsed taskiq message.
        """
        raise NotImplementedError
