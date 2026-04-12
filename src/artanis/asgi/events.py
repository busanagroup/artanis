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


import dataclasses
import typing as t


@dataclasses.dataclass
class Events:
    """Application events register."""

    startup: list[t.Callable[..., t.Coroutine[t.Any, t.Any, None]]] = dataclasses.field(default_factory=list)
    shutdown: list[t.Callable[..., t.Coroutine[t.Any, t.Any, None]]] = dataclasses.field(default_factory=list)

    def register(self, event: str, handler: t.Callable) -> None:
        """Register a new event.

        :param event: Event type.
        :param handler: Event handler.
        """
        assert event in {f.name for f in dataclasses.fields(self)}, f"Wrong event: {event}."
        getattr(self, event).append(handler)

    @classmethod
    def build(cls, **events: list[t.Callable[..., t.Coroutine[t.Any, t.Any, None]]]) -> "Events":
        """Build events register from dict.

        :param events: Events to register.
        :return: Events instance.
        """
        keys = set(events.keys()) - {f.name for f in dataclasses.fields(cls)}
        assert not keys, f"Wrong event{'s' if len(keys) > 1 else ''}: {', '.join(keys)}."
        return cls(**events)
