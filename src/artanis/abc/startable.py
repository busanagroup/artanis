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
# the Apache-2.0 License: https://www.apache.org/licenses/LICENSE-2.0\
from __future__ import annotations

__all__ = ['Startable', 'AsyncStartable', 'StartableManager',
           'AsyncStartableManager', 'StartableListener', 'AsyncStartableListener',
           'LifeCycleManager', 'AsyncLifeCycleManager']

import asyncio
import logging
import typing

from artanis.abc.configurable import ConfigurableListener, Configurable, AsyncConfigurableListener, AsyncConfigurable
from artanis.abc.listenable import BaseListener, Listenable, FailureListener, Failable, AsyncFailureListener
from artanis.abc.objlock import SyncLock, AsyncLock
from artanis.abc.singleton import Singleton, AsyncSingleton


class BaseStartableListener(BaseListener):
    """A Listener support class to provide bridge of state changing behaviour on Startable Object"""

    def __init__(self, starting_func=None, started_func=None, stopping_func=None, stopped_func=None, **kwargs):
        """
        Initialize the listener
        @param starting_func: callback function when fired upon observable object starting
        @param started_func: callback function when fired upon observable object started
        @param failure_func: callback function when fired upon observable object failure
        @param stopping_func: callback function when fired upon observable object stopping
        @param stopped_func: callback function when fired upon observable object stopped
        @param configuring_func: callback function when fired upon observable object configuring
        @param configured_func: callback function when fired upon observable object configured
        """
        super(BaseStartableListener, self).__init__(**kwargs)
        self._starting = starting_func
        self._started = started_func
        self._stopping = stopping_func
        self._stopped = stopped_func

    def on_starting(self, obj):
        """Facilitating to notify observer upon starting event"""
        self._starting(obj) if self._starting else None

    def on_started(self, obj):
        """Facilitating to notify observer upon started event"""
        self._started(obj) if self._started else None

    def on_stopping(self, obj):
        """Facilitating to notify observer upon stopping event"""
        self._stopping(obj) if self._stopping else None

    def on_stopped(self, obj):
        """Facilitating to notify observer upon stopped event"""
        self._stopped(obj) if self._stopped else None

    def get_on_starting(self):
        """Get on Starting Event handler"""
        return self._starting

    def set_on_starting(self, starting_func):
        """Set on Starting Event handler"""
        self._starting = starting_func

    def get_on_started(self):
        """Get on Started Event handler"""
        return self._started

    def set_on_started(self, started_func):
        """Set on Started Event handler"""
        self._started = started_func

    def get_on_stopping(self):
        """Get on Stopping Event handler"""
        return self._stopping

    def set_on_stopping(self, stopping_func):
        """Set on Stopping Event handler"""
        self._stopping = stopping_func

    def get_on_stopped(self):
        """Get on Stopped Event handler"""
        return self._stopped

    def set_on_stopped(self, stopped_func):
        """Set on Started Event handler"""
        self._stopped = stopped_func


class StartableListener(BaseStartableListener, FailureListener, ConfigurableListener):
    ...


class AsyncStartableListener(BaseStartableListener, AsyncFailureListener, AsyncConfigurableListener):

    async def on_starting(self, obj):
        """Facilitating to notify observer upon starting event"""
        if self._starting:
            if asyncio.iscoroutinefunction(self._starting):
                await self._starting(obj)
            else:
                self._starting(obj)

    async def on_started(self, obj):
        """Facilitating to notify observer upon started event"""
        if self._started:
            if asyncio.iscoroutinefunction(self._started):
                await self._started(obj)
            else:
                self._started(obj)

    async def on_stopping(self, obj):
        """Facilitating to notify observer upon stopping event"""
        if self._stopping:
            if asyncio.iscoroutinefunction(self._stopping):
                await self._stopping(obj)
            else:
                self._stopping(obj)

    async def on_stopped(self, obj):
        """Facilitating to notify observer upon stopped event"""
        if self._stopped:
            if asyncio.iscoroutinefunction(self._stopped):
                await self._stopped(obj)
            else:
                self._stopped(obj)


class BaseStartable(Failable, Listenable):
    """An Abstract Class for generic startable component"""

    FAILED, STOPPED, STARTING, STARTED, STOPPING = -1, 0, 1, 2, 3

    def __init__(self, config=None):
        super(BaseStartable, self).__init__(config=config)
        """Initialize the component, configuration object is optional which could be added by set_configuration later"""
        self._state = BaseStartable.STOPPED
        self._enabled = True

    def is_enabled(self) -> bool:
        """
        Check if the component is enable
        @return: boolean value
        """
        return self._enabled

    def is_started(self) -> bool:
        """
        Check if the component is started
        @return: boolean value
        """
        return self._state == BaseStartable.STARTED

    def is_starting(self) -> bool:
        """
        Check if the component is starting
        @return: boolean value
        """
        return self._state == BaseStartable.STARTING

    def is_stopped(self) -> bool:
        """
        Check if the component is stopped
        @return: boolean value
        """
        return self._state == BaseStartable.STOPPED

    def is_stopping(self) -> bool:
        """
        Check if the component is stopping
        @return: boolean value
        """
        return self._state == BaseStartable.STOPPING

    def is_running(self) -> bool:
        """
        Ceck if the component is running
        @return: boolean value
        """
        return self.is_started() or self.is_starting()

    def state_in(self, states: typing.List):
        return self._state in states

    def _set_starting(self):
        self._state = BaseStartable.STARTING
        for listener in self.get_listeners():
            listener.on_starting(self)

    def _set_started(self):
        self._state = BaseStartable.STARTED
        for listener in self.get_listeners():
            listener.on_started(self)

    def _set_stopping(self):
        self._state = BaseStartable.STOPPING
        for listener in self.get_listeners():
            listener.on_stopping(self)

    def _set_stopped(self):
        self._state = BaseStartable.STOPPED
        for listener in self.get_listeners():
            listener.on_stopped(self)

    def _set_failed(self, ex: Exception):
        self._state = BaseStartable.STOPPED
        super(BaseStartable, self)._set_failed(ex)

    @property
    def service_enabled(self):
        return self.is_enabled()

    @service_enabled.setter
    def service_enabled(self, value):
        self._enabled = value


class Startable(BaseStartable, Configurable):
    """An Abstract Class for generic startable component"""

    def do_beforestart(self):
        """An abstract method to perform before start routines"""
        ...

    def do_start(self):
        """An abstract method to perform component start routines"""
        ...

    def do_afterstart(self):
        """An abstract method to perform after start routines"""
        ...

    def do_beforestop(self):
        """An abstract method to perform before stop routines"""
        ...

    def do_stop(self):
        """An abstract method to perform component stop routines"""
        ...

    def do_afterstop(self):
        """An abstract method to perform after start routines"""
        ...

    def configure(self):
        """Perform configuring this component"""
        if self.state_in([Startable.CONFIGURED, Startable.CONFIGURING]):
            return
        try:
            super(Startable, self).configure()
        except Exception as exc:
            self._set_failed(exc)
            raise exc

    def start(self):
        """Perform Starting this component"""
        self.configure() if not self.is_configured() else None
        self.do_beforestart()
        lock = self.get_lock()
        lock.acquire()
        try:
            if (not self._enabled) or (self.state_in([Startable.STARTED, Startable.STARTING])):
                return
            self._set_starting()
            self.do_start()
            self._set_started()
        except Exception as exc:
            self._set_failed(exc)
            raise exc
        finally:
            lock.release()
            self.do_afterstart()

    def stop(self):
        """Perform Stopping this component"""
        self.do_beforestop()
        lock = self.get_lock()
        lock.acquire()
        try:
            if self.state_in([Startable.STOPPED, Startable.STOPPING]):
                return
            self._set_stopping()
            self.do_stop()
            self._set_stopped()
        except Exception as exc:
            self._set_failed(exc)
            raise exc
        finally:
            lock.release()
            self.do_afterstop()


class AsyncStartable(BaseStartable, AsyncConfigurable):
    """An Abstract Class for generic startable component"""

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

    async def configure(self):
        """Perform configuring this component"""
        if self.state_in([AsyncStartable.CONFIGURED, AsyncStartable.CONFIGURING]):
            return
        try:
            await super(AsyncStartable, self).configure()
        except Exception as exc:
            await self._set_failed(exc)
            raise exc

    async def start(self):
        """Perform Starting this component"""
        self.configure() if not self.is_configured() else None
        await self.do_beforestart()
        lock = self.get_lock()
        await lock.acquire()
        try:
            if (not self._enabled) or (self._state in [AsyncStartable.STARTED, AsyncStartable.STARTING]):
                return
            await self._set_starting()
            await self.do_start()
            await self._set_started()
        except Exception as exc:
            await self._set_failed(exc)
            raise exc
        finally:
            lock.release()
            await self.do_afterstart()

    async def stop(self):
        """Perform Stopping this component"""
        await self.do_beforestop()
        lock = self.get_lock()
        await lock.acquire()
        try:
            if self.state_in([AsyncStartable.STOPPED, AsyncStartable.STOPPING]):
                return
            await self._set_stopping()
            await self.do_stop()
            await self._set_stopped()
        except Exception as exc:
            await self._set_failed(exc)
            raise exc
        finally:
            self.lock.release()
            await self.do_afterstop()

    async def _set_starting(self):
        self._state = BaseStartable.STARTING
        for listener in self.get_listeners():
            start_func = listener.on_starting
            if asyncio.iscoroutinefunction(start_func):
                await start_func(self)
            else:
                start_func(self)

    async def _set_started(self):
        self._state = BaseStartable.STARTED
        for listener in self.get_listeners():
            start_func = listener.on_started
            if asyncio.iscoroutinefunction(start_func):
                await start_func(self)
            else:
                start_func(self)

    async def _set_stopping(self):
        self._state = BaseStartable.STOPPING
        for listener in self.get_listeners():
            start_func = listener.on_stopping
            if asyncio.iscoroutinefunction(start_func):
                await start_func(self)
            else:
                start_func(self)

    async def _set_stopped(self):
        self._state = BaseStartable.STOPPED
        for listener in self.get_listeners():
            start_func = listener.on_stopped
            if asyncio.iscoroutinefunction(start_func):
                await start_func(self)
            else:
                start_func(self)

    async def _set_failed(self, ex: Exception):
        self._state = BaseStartable.STOPPED
        for listener in self.get_listeners():
            start_func = listener.on_failure
            if asyncio.iscoroutinefunction(start_func):
                await start_func(self, ex)
            else:
                start_func(self, ex)


class BaseStartableManager(object):

    def __init__(self, config=None):
        super(BaseStartableManager, self).__init__(config=config)
        self._startable_objects = list()

    def get_objects(self):
        return self._startable_objects

    def get_object(self, cls):
        if cls:
            for item in self._startable_objects:
                if isinstance(item, cls):
                    return item
        return None


class StartableManager(BaseStartableManager, Startable):

    def add_object(self, obj):
        if (not obj) or (not isinstance(obj, Startable)):
            return
        if obj not in self._startable_objects:
            self._startable_objects.append(obj)

        try:
            if self.is_running():
                obj.set_configuration(self.get_configuration())
                obj.start()
        except Exception as exc:
            raise RuntimeError(exc)

    def remove_object(self, obj):
        if (not obj) or (not isinstance(obj, Startable)):
            return
        if obj in self._startable_objects:
            obj_pos = self._startable_objects.index(obj)
            self._startable_objects.pop(obj_pos)
            obj.stop()

    def do_configure(self):
        for item in self._startable_objects:
            try:
                item.set_configuration(self.get_configuration())
                item.configure()
            except Exception as exc:
                logging.error(exc)

    def do_start(self):
        for item in self._startable_objects:
            try:
                item.start()
            except Exception as exc:
                logging.error(exc)

    def do_stop(self):
        for item in reversed(self._startable_objects):
            try:
                item.stop()
            except Exception as exc:
                logging.error(exc)


class AsyncStartableManager(BaseStartableManager, AsyncStartable):

    async def add_object(self, obj):
        if (not obj) or (not isinstance(obj, AsyncStartable)):
            return
        if obj not in self._startable_objects:
            self._startable_objects.append(obj)

        try:
            if self.is_running():
                obj.set_configuration(self.get_configuration())
                await obj.start()
        except Exception as exc:
            raise RuntimeError(exc)

    async def remove_object(self, obj):
        if (not obj) or (not isinstance(obj, AsyncStartable)):
            return
        if obj in self._startable_objects:
            obj_pos = self._startable_objects.index(obj)
            self._startable_objects.pop(obj_pos)
            await obj.stop()

    async def do_configure(self):
        for item in self._startable_objects:
            try:
                item.set_configuration(self.get_configuration())
                await item.configure()
            except Exception as exc:
                logging.error(exc)

    async def do_start(self):
        for item in self._startable_objects:
            try:
                await item.start()
            except Exception as exc:
                logging.error(exc)

    async def do_stop(self):
        for item in reversed(self._startable_objects):
            try:
                await item.stop()
            except Exception as exc:
                logging.error(exc)


class LifeCycleManager(StartableManager, Singleton, SyncLock):
    ...


class AsyncLifeCycleManager(AsyncStartableManager, AsyncSingleton, AsyncLock):
    ...
