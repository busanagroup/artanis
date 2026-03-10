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

__all__ = ['BaseListenable', 'Listenable', 'Failable', 'BaseListener', 'FailureListener',
           'AsyncFailureListener', 'AsyncFailable']

import asyncio
from abc import ABC, abstractmethod


class BaseListener(ABC):
    ...


class FailureListener(BaseListener):

    def __init__(self, failure_func=None, **kwargs):
        """
        Initialize Failure listener
        @param failure_func: callback function when fired upon observable object failure
        """
        super(FailureListener, self).__init__(**kwargs)
        self._failure = failure_func

    def on_failure(self, obj, exc):
        """Facilitating to notify observer upon failure event"""
        self._failure(obj, exc) if self._failure else None

    def set_on_failure(self, failure_func):
        """Set on Failure Event handler"""
        self._failure = failure_func

    def get_on_failure(self):
        """Get on Failure Event handler"""
        return self._failure


class AsyncFailureListener(FailureListener):

    async def on_failure(self, obj, exc):
        """Facilitating to notify observer upon failure event"""
        if self._failure:
            if asyncio.iscoroutinefunction(self._failure):
                await self._failure(obj, exc)
            else:
                self._failure(obj, exc)


class BaseListenable(ABC):

    @abstractmethod
    def get_listeners(self):
        raise NotImplementedError()


class Failable(BaseListenable):

    def _set_failed(self, ex: Exception):
        for listener in self.get_listeners():
            listener.on_failure(self, ex)


class AsyncFailable(Failable):

    async def _set_failed(self, ex: Exception):
        for listener in self.get_listeners():
            failure_func = listener.on_failure
            if asyncio.iscoroutinefunction(failure_func):
                await failure_func(self, ex)
            else:
                failure_func(self, ex)


class Listenable(BaseListenable):

    def __init__(self, *args, **kwargs):
        super(Listenable, self).__init__(*args, **kwargs)
        self._listeners = list()

    def add_listener(self, listener):
        """Add listener to this observable component"""
        self._listeners.append(listener) if isinstance(listener, BaseListener) else None

    def remove_listener(self, listener):
        """Remove listener from this observable component"""
        if isinstance(listener, BaseListener) and (listener in self._listeners):
            obj_pos = self._listeners.index(listener)
            self._listeners.pop(obj_pos)

    def get_listeners(self):
        return self._listeners if hasattr(self, '_listeners') else list()
