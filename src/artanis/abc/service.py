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
# This module is part of Centric PLM Integration Bridge and is released under
# the Apache-2.0 License: https://www.apache.org/licenses/LICENSE-2.0

from __future__ import annotations

import asyncio
import typing

from artanis.abc.configurable import Configurable


class StartableService(Configurable):
    FAILED, STOPPED, STARTING, STARTED, STOPPING = -1, 0, 1, 2, 3

    def __init__(self, *args, **kwargs):
        super(StartableService, self).__init__(*args, **kwargs)
        self._state = self.STOPPED
        self._enabled = True

    async def do_beforestart(self):
        """An abstract method to perform before start routines"""
        ...

    async def do_start(self):
        """An abstract method to perform component start routines"""
        ...

    async def do_afterstart(self):
        """An abstract method to perform after start routines"""
        ...

    async def do_beforestop(self):
        """An abstract method to perform before stop routines"""
        ...

    async def do_stop(self):
        """An abstract method to perform component stop routines"""
        ...

    async def do_afterstop(self):
        """An abstract method to perform after start routines"""
        ...

    async def start(self):
        """Perform Starting this component"""
        await self.do_beforestart()
        try:
            if (not self._enabled) or (self._state in [self.STARTED, self.STARTING]):
                return
            await self._set_starting()
            await self.do_start()
            await self._set_started()
        except Exception as exc:
            await self._set_failed(exc)
            raise exc
        finally:
            await self.do_afterstart()

    def state_in(self, states: typing.List):
        return self._state in states

    async def stop(self):
        """Perform Stopping this component"""
        await self.do_beforestop()
        try:
            if self.state_in([self.STOPPED, self.STOPPING]):
                return
            await self._set_stopping()
            await self.do_stop()
            await self._set_stopped()
        except Exception as exc:
            await self._set_failed(exc)
            raise exc
        finally:
            await self.do_afterstop()

    async def _set_starting(self):
        self._state = self.STARTING
        for listener in self.get_listeners():
            start_func = listener.on_starting
            if asyncio.iscoroutinefunction(start_func):
                await start_func(self)
            else:
                start_func(self)

    async def _set_started(self):
        self._state = self.STARTED
        for listener in self.get_listeners():
            start_func = listener.on_started
            if asyncio.iscoroutinefunction(start_func):
                await start_func(self)
            else:
                start_func(self)

    async def _set_stopping(self):
        self._state = self.STOPPING
        for listener in self.get_listeners():
            start_func = listener.on_stopping
            if asyncio.iscoroutinefunction(start_func):
                await start_func(self)
            else:
                start_func(self)

    async def _set_stopped(self):
        self._state = self.STOPPED
        for listener in self.get_listeners():
            start_func = listener.on_stopped
            if asyncio.iscoroutinefunction(start_func):
                await start_func(self)
            else:
                start_func(self)

    async def _set_failed(self, ex: Exception):
        self._state = self.STOPPED
        for listener in self.get_listeners():
            start_func = listener.on_failure
            if asyncio.iscoroutinefunction(start_func):
                await start_func(self, ex)
            else:
                start_func(self, ex)

    def is_enabled(self) -> bool:
        """
        Check if the component is enable
        @return: boolean value
        """
        return self._enabled

    @property
    def service_enabled(self):
        return self.is_enabled()

    @service_enabled.setter
    def service_enabled(self, value):
        self._enabled = value
