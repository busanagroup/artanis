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

__all__ = ['BaseConfigurable', 'Configurable', 'ConfigurableListener',
           'AsyncConfigurable', 'AsyncConfigurableListener']

import asyncio
from .listenable import Listenable, BaseListener
from .objlock import BaseLocker


class ConfigurableListener(BaseListener):

    def __init__(self, configuring_func=None, configured_func=None, **kwargs):
        super(ConfigurableListener, self).__init__(**kwargs)
        self._configuring = configuring_func
        self._configured = configured_func

    def on_configuring(self, obj, config):
        """Facilitating to notify observer upon configuring event"""
        self._configuring(obj, config) if self._configuring else None

    def on_configured(self, obj, config):
        """Facilitating to notify observer upon configured event"""
        self._configured(obj, config) if self._configured else None

    def get_on_configuring(self):
        """Get on Configuring Event handler"""
        return self._configuring

    def set_on_configuring(self, configuring_func):
        """Set on Configuring Event handler"""
        self._configuring = configuring_func

    def get_on_configured(self):
        """Get on Configured Event handler"""
        return self._configured

    def set_on_configured(self, configured_func):
        """Set on Configured Event handler"""
        self._configured = configured_func


class AsyncConfigurableListener(ConfigurableListener):

    async def on_configuring(self, obj, config):
        """Facilitating to notify observer upon configuring event"""
        if self._configuring:
            if asyncio.iscoroutinefunction(self._configuring):
                await self._configuring(obj, config)
            else:
                self._configuring(obj, config)

    async def on_configured(self, obj, config):
        """Facilitating to notify observer upon configured event"""
        if self._configured:
            if asyncio.iscoroutinefunction(self._configured):
                await self._configured(obj, config)
            else:
                self._configured(obj, config)


class BaseConfigurable(Listenable):
    UNCONFIGURED, CONFIGURING, CONFIGURED = 0, 1, 2

    def __init__(self, *args, config=None, **kwargs):
        """Initialize the component, configuration object is optional which could be added by set_configuration later"""
        super(BaseConfigurable, self).__init__(*args, **kwargs)
        self._configuration = config
        self._configured = BaseConfigurable.UNCONFIGURED
        self._use_lock = True

    def configure(self):
        raise NotImplementedError()

    @property
    def apply_lock(self) -> bool:
        return self._use_lock

    @apply_lock.setter
    def apply_lock(self, value):
        self._use_lock = value

    def is_configured(self) -> bool:
        return self._configured != BaseConfigurable.UNCONFIGURED

    def get_configuration(self) -> 'Configuration':
        """
        Get the configuration object commonly rfequired upon configuring component
        @return:
        """
        return self._configuration

    def set_configuration(self, config: 'Configuration'):
        """Set the configuration dictionary commonly required upon configuring this component"""
        self._configuration = config

    def get_config_value(self, key, def_value):
        assert self._configuration is not None, "This object has not been configured properly"
        return self._configuration.get_property_value(key, def_value)

    def _set_configured(self):
        self._configured = BaseConfigurable.CONFIGURED
        config = self.get_configuration()
        for listener in self.get_listeners():
            listener.on_configured(self, config)

    def _set_configuring(self):
        self._configured = BaseConfigurable.CONFIGURING
        config = self.get_configuration()
        for listener in self.get_listeners():
            listener.on_configuring(self, config)


class Configurable(BaseConfigurable, BaseLocker):

    def do_configure(self):
        """An abstract method to perform component configuring routines"""
        ...

    def configure(self):
        """Perform configuring this component"""
        lock = None
        if self.apply_lock:
            lock = self.get_lock()
            lock.acquire()
        try:
            if self._configured == Configurable.CONFIGURED:
                return
            self._set_configuring()
            self.do_configure()
            self._set_configured()
        except Exception as exc:
            raise exc
        finally:
            if self.apply_lock:
                lock.release()


class AsyncConfigurable(BaseConfigurable, BaseLocker):

    async def do_configure(self):
        """An abstract method to perform component configuring routines"""
        ...

    async def configure(self):
        """Perform configuring this component"""
        lock = None
        if self.apply_lock:
            lock = self.get_lock()
            await lock.acquire()
        try:
            if self._configured == Configurable.CONFIGURED:
                return
            await self._set_configuring()
            await self.do_configure()
            await self._set_configured()
        except Exception as exc:
            raise exc
        finally:
            if self.apply_lock:
                lock.release()

    async def _set_configured(self):
        self._configured = BaseConfigurable.CONFIGURED
        config = self.get_configuration()
        for listener in self.get_listeners():
            config_func = listener.on_configured
            if asyncio.iscoroutinefunction(config_func):
                await config_func(self, config)
            else:
                config_func(self, config)

    async def _set_configuring(self):
        self._configured = BaseConfigurable.CONFIGURING
        config = self.get_configuration()
        for listener in self.get_listeners():
            config_func = listener.on_configuring
            if asyncio.iscoroutinefunction(config_func):
                await config_func(self, config)
            else:
                config_func(self, config)
