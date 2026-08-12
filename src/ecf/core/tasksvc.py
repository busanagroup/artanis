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

from artanis.abc.configurable import AsyncConfigurable
from artanis.taskiq.proxy import TaskObjectProxy
from ecf.core.ecfcmn import SupportClass

__all__ = ['TaskHandler', 'TaskCaller', 'ReturnableTaskCaller']


class TaskCaller(TaskObjectProxy): ...


class ReturnableTaskCaller(TaskCaller):
    def __init__(self, username: str, service_name: str, timeout: int = 30):
        super().__init__(username, service_name)
        self.timeout = timeout

    async def __submit(self, func_name: str, *args, **kwargs):
        task = await super(ReturnableTaskCaller, self).__submit(func_name, *args, **kwargs)
        return await task.wait_result(timeout=self.timeout)


class TaskHandler(AsyncConfigurable, SupportClass):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service_name = self.__class__.__name__

    def get_service_name(self) -> str:
        return self.service_name
