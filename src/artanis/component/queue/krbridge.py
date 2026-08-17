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
import json
import typing as t

from artanis.sqlentity.encoder import JSON_DUMPS

if t.TYPE_CHECKING:
    from artanis.component.queue.quesend import QueueSubmitter


class KRBSubmitter(QueueSubmitter):
    __task_name: str = "artanis_krbsend"


class MessageMode(enum.Enum):
    COMMAND = 0
    EVENT = 1


class BaseMessage:

    @staticmethod
    def _decode(message: str):
        command = str(base64.b64decode(message), "utf-8")
        return json.loads(command)

    @staticmethod
    def _encode(message: dict[str, t.Any] | list[t.Any] | tuple[t.Any] | str):
        if isinstance(message, dict):
            command_str = JSON_DUMPS(message)
        elif isinstance(message, list):
            command_str = JSON_DUMPS(message)
        elif isinstance(message, tuple):
            command_str = JSON_DUMPS(message)
        else:
            command_str = str(message).encode("utf-8")
        return command_str

    def setup(self, message: dict[str, t.Any]):
        pass


class MessageCommand(BaseMessage):

    def __init__(
            self,
            module: str | None = None,
            submodule: str | None = None,
            command: str | None = None,
            params: t.Any | None = None,
            message: str | None = None,
    ):
        self.module = module
        self.submodule = submodule
        self.command = command
        self.params = params
        if isinstance(message, str):
            cmddict = self._decode(message)
            self.setup(cmddict)

    def parameters(self, *args, **kwargs):
        self.params = [args, kwargs]

    def setup(self, message: dict[str, t.Any]):
        _cmddict = message if isinstance(message, dict) else None
        if isinstance(_cmddict, dict):
            self.module = self.module if 'module' not in _cmddict else _cmddict['module']
            self.submodule = self.submodule if 'submodule' not in _cmddict else _cmddict['submodule']
            self.command = self.command if 'command' not in _cmddict else _cmddict['command']
            self.params = self.params if 'data' not in _cmddict else _cmddict['data']

    def __dict__(self):
        return {
            'msgtype': MessageMode.COMMAND.value,
            'module': self.module,
            'submodule': self.submodule,
            'command': self.command,
            'data': self.params
        }

    def encode(self):
        return self._encode(self.__dict__())

    def decode(self, message: str | None = None):
        cmddict = self._decode(message)
        self.setup(cmddict)


class MessageNotifier(BaseMessage):

    def __init__(
            self,
            module: str | None = None,
            submodule: str | None = None,
            event: str | None = None,
            params: str | None = None,
            message: str | None = None):
        self.module = module
        self.submodule = submodule
        self.event = event
        self.params = params
        if isinstance(message, str):
            cmddict = self._decode(message)
            self.setup(cmddict)

    def parameters(self, *args, **kwargs):
        self.params = [args, kwargs]

    def setup(self, message: dict[str, t.Any]):
        _msgdict = message if isinstance(message, dict) else None
        if isinstance(_msgdict, dict):
            self.module = self.module if 'module' not in _msgdict else _msgdict['module']
            self.submodule = self.submodule if 'submodule' not in _msgdict else _msgdict['submodule']
            self.event = self.event if 'event' not in _msgdict else _msgdict['event']
            self.params = self.params if 'data' not in _msgdict else _msgdict['data']

    def encode(self):
        return self._encode(dict(self))

    def decode(self, message: str | None = None):
        evtdict = self._decode(message)
        self.setup(evtdict)


class MessageFactory(BaseMessage):
    klass_list = [MessageCommand, MessageNotifier]

    @classmethod
    def get_klass(cls, msg_type: int):
        return cls.klass_list[msg_type] if msg_type < len(cls.klass_list) else None

    @classmethod
    def instantiate(cls, klass):
        obj = object.__new__(klass)
        obj.__init__()
        return obj

    @classmethod
    def generate(cls, message):
        cmddict = cls._decode(message) if isinstance(message, str) else message if isinstance(message, dict) else None
        klass = cls.get_klass(cmddict['msgtype']) if cmddict and ('msgtype' in cmddict) else None
        obj: BaseMessage | None = t.cast(BaseMessage, cls.instantiate(klass)) if klass else None
        if not obj:
            return None
        obj.setup(cmddict)
        return obj
