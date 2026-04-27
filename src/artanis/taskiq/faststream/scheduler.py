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

from typing import TYPE_CHECKING

from taskiq.scheduler.scheduled_task import ScheduledTask
from taskiq.scheduler.scheduler import TaskiqScheduler as Scheduler
from taskiq.utils import maybe_awaitable

from .kicker import LabelRespectKicker

if TYPE_CHECKING:  # pragma: no cover
    from taskiq.abc.schedule_source import ScheduleSource


class StreamScheduler(Scheduler):
    """Patched scheduler with custom kicker."""

    async def on_ready(self, source: "ScheduleSource", task: ScheduledTask) -> None:
        """
        This method is called when task is ready to be enqueued.

        It's triggered on proper time depending on `task.cron` or `task.time` attribute.
        :param task: task to send
        """
        await maybe_awaitable(source.pre_send(task))
        await LabelRespectKicker(task.task_name, self.broker, task.labels).kiq(
            *task.args,
            **task.kwargs,
        )
        await maybe_awaitable(source.post_send(task))
