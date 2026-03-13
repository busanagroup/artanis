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
# the Apache-2.0 License: https://www.apache.org/licenses/LICENSE-2.0

__all__ = ['BaseLocker', 'SyncLock', 'AsyncLock']

from asyncio import Lock
from threading import RLock


class BaseLocker(object):

    def __init__(self, *args, **kwargs):
        super(BaseLocker, self).__init__(*args, **kwargs)

    def get_lock(self):
        raise NotImplementedError()

    def is_async(self):
        return False

    @classmethod
    def get_class_locker(cls):
        raise NotImplementedError

    @property
    def lock(self):
        return self.get_lock()


class SyncLock(BaseLocker):
    class_locker = None

    def __init__(self, *args, **kwargs):
        super(SyncLock, self).__init__(*args, **kwargs)
        self._lock = None

    def get_lock(self):
        if not self._lock:
            self._lock = RLock()
        return self._lock

    @classmethod
    def get_class_locker(cls):
        if not cls.class_locker:
            cls.class_locker = RLock()
        return cls.class_locker


class AsyncLock(BaseLocker):
    class_locker = None

    def __init__(self, *args, **kwargs):
        super(AsyncLock, self).__init__(*args, **kwargs)
        self._lock = None

    def get_lock(self):
        if not self._lock:
            self._lock = Lock()
        return self._lock

    def is_async(self):
        return True

    @classmethod
    def get_class_locker(cls):
        if not cls.class_locker:
            cls.class_locker = Lock()
        return cls.class_locker
