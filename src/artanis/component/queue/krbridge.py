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
import base64
import enum
import typing as t

from artanis.component.queue.quesend import QueueSubmitter
from artanis.component.queue.types import QueueType
from artanis.config import Configuration
from artanis.events import BaseEvent


class MessageMode(enum.Enum):
    COMMAND = 0
    EVENT = 1


class KRBMessageEvent(BaseEvent, event_type="com.busanagroup.bridge.event"):
    module: str
    submodule: str
    event: str
    param_args: tuple[t.Any, ...] | tuple[()] = ()
    param_kwargs: dict = {}


class KRBMessageCommand(BaseEvent, event_type="com.busanagroup.bridge.command"):
    module: str
    submodule: str
    command: str
    param_args: tuple[t.Any, ...] | tuple[()] = ()
    param_kwargs: dict = {}


class KRBridgeSubmitter(QueueSubmitter):

    def get_task_name(self) -> str:
        return "artanis_krbridge"

    def get_queue_type(self) -> int:
        return QueueType.KR_BRIDGE.value


class BaseMessage:

    def __init__(
            self,
            module: str,
            submodule: str
    ):
        self.module: str = module
        self.submodule: str = submodule
        config = Configuration.get_default_instance(create_instance=False)
        self.exchange_name = config.get_property_value(config.ARTANIS_MQ_EXCHANGE_KRB, "artanis.krbridge")

    def _encode(self, data: bytes) -> str:
        return base64.b64encode(data).decode("utf-8")


class KRBEventSender(BaseMessage):

    async def notify(self, event: str, *args, **kwargs):
        evt_message = KRBMessageEvent(
            module=self.module,
            submodule=self.submodule,
            event=event,
            param_args=args,
            param_kwargs=kwargs
        )
        route_key = f"{evt_message.event_type}.{self.module}.{self.submodule}"
        message = evt_message.model_dump(mode="json")
        await KRBridgeSubmitter(self.exchange_name, route_key, message, execute_immediately=True)


class _CommandMethod:

    def __init__(self, send: t.Callable, method_name: str):
        self._method_name = method_name
        self._send = send

    async def __call__(self, *args, **kwargs):
        return await self._send(self._method_name, *args, **kwargs)


class KRBCommandSender(BaseMessage):

    def __getattr__(self, func_name: str):
        return _CommandMethod(self.execute, func_name)

    async def execute(self, command: str, *args, **kwargs):
        cmd_message = KRBMessageCommand(
            module=self.module,
            submodule=self.submodule,
            command=command,
            param_args=args,
            param_kwargs=kwargs
        )
        route_key = f"{cmd_message.event_type}.{self.module}.{self.submodule}"
        message = cmd_message.model_dump(mode="json")
        await KRBridgeSubmitter(self.exchange_name, route_key, message, execute_immediately=True)
