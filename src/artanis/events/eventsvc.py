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
import enum
import inspect
import typing as t

from artanis import events
from artanis.abc.configurable import Configurable
from artanis.config import Configuration
from artanis.events import topic, EventBus


class Match(enum.Enum):
    none = enum.auto()
    partial = enum.auto()
    full = enum.auto()


class EventDescriptor:
    name: str
    path: events.Topic | str

    class Match(enum.Enum):
        none = enum.auto()
        partial = enum.auto()
        full = enum.auto()

    def describe(self, name: str, path: str | None = None) -> None:
        self.name = name
        self.path = events.Topic(self.name if path is None else path)

    def match(self, event_type: str) -> tuple[str, Match]:
        """Check if this route matches with given scope.

        :param event_type.
        :return: Match.
        """
        m = self.path.match(event_type)
        path = str(topic.Topic("/") / (m.unmatched or ""))
        return path, Match.full if m.match in (self.path.Match.exact, self.path.Match.partial) else Match.none


class EventCapture:

    def __init__(
            self,
            path: str | events.Topic | list[str] | None = None,
            name: str | None = None,
    ):
        if not path or isinstance(path, str):
            self.path = [events.Topic(name if path is None else path)]
        else:
            self.path = [events.Topic(p) for p in path]
        self.name = name

    def match(self, event_type: str) -> Match:
        m = Match.none
        for topic in self.path:
            m = Match.full if topic.match(event_type).match == topic.Match.exact else Match.none
            if m == Match.full:
                break
        return m


def get_name(endpoint: t.Callable[..., t.Any]) -> str:
    return getattr(endpoint, "__name__", endpoint.__class__.__name__)


def on_event(
        func: t.Callable[..., t.Any] | None = None,
        event_type: str | events.Topic | list[str] | None = None,
        name: str | None = None,
) -> t.Callable[..., t.Any]:
    if func:
        _name = get_name(func)
        func.event = EventCapture(
            event_type,
            _name if name is None else name
        )
        return func
    else:
        def wrapper(fnc):
            _name = get_name(fnc)
            fnc.event = EventCapture(
                event_type,
                _name if name is None else name
            )
            return fnc

        return wrapper


def has_event(cls):
    for func_name, func in cls.__dict__.items():
        if hasattr(func, "event"):
            return True
    return False


class EventHandlerABC(Configurable):
    descriptor: EventDescriptor = EventDescriptor

    def __init__(
            self,
            *args,
            **kwargs):
        config = kwargs.pop("config", None) or Configuration.get_default_instance(create_instance=False)
        super().__init__(*args, config=config, **kwargs)
        for descriptor in self.handler_methods:
            func = getattr(self, descriptor.name)
            descriptor.app = func

    def __init_subclass__(cls, **kwargs):
        event_type = kwargs.pop('event_type', None)
        cls.handle_events = has_event(cls)
        if hasattr(cls, "descriptor"):
            klass = EventDescriptor if cls.descriptor is None else \
                cls.descriptor if inspect.isclass(cls.descriptor) else \
                    cls.descriptor.__class__
            cls.descriptor = klass()
            cls.descriptor.describe(cls.__name__, event_type)
        cls.handler_methods = []
        for _, func in cls.__dict__.items():
            if hasattr(func, "event"):
                descriptor = func.event
                cls.handler_methods.append(descriptor)
                del func.event


    @classmethod
    def get_event_handler(cls, event_type: str) -> list[tuple[str, str]] | None:
        handler_list = []
        descriptor = cls.descriptor
        event, match = descriptor.match(event_type)
        if match != Match.full:
            return handler_list
        for handler in cls.handler_methods:
            match = handler.match(event)
            if match == Match.full:
                handler_list.append((descriptor.name, handler.name))
        return handler_list

    @property
    def eventbus(self) -> EventBus:
        config = self.get_configuration()
        return config.container.eventbus






