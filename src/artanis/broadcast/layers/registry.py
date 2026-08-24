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
from __future__ import annotations

from artanis.broadcast.layers.base import BaseChannelLayer


class ChannelLayerRegistry:
    """
    Registry pattern for managing channel layers.
    Allows direct registration of channel layer instances.
    """

    def __init__(self) -> None:
        self._layers: dict[str, BaseChannelLayer] = {}

    def register(self, alias: str, layer: BaseChannelLayer) -> None:
        """
        Register a channel layer instance with an alias.

        Args:
            alias: Name to register the layer under
            layer: Channel layer instance
        """
        self._layers[alias] = layer

    def unregister(self, alias: str) -> None:
        """
        Remove a channel layer from the registry.
        """
        if alias in self._layers:
            del self._layers[alias]

    def get(self, alias: str) -> BaseChannelLayer | None:
        """
        Get a channel layer by alias.
        """
        return self._layers.get(alias)

    def list_aliases(self) -> list[str]:
        """
        Get all registered aliases.
        """
        return list(self._layers.keys())

    def clear(self) -> None:
        """
        Clear all registered layers.
        """
        self._layers.clear()

    def __contains__(self, alias: str) -> bool:
        """Check if a channel layer alias is registered.

        Args:
            alias: The channel layer alias to check.

        Returns:
            True if the alias is registered, False otherwise.
        """
        return alias in self._layers

    def __getitem__(self, alias: str) -> BaseChannelLayer:
        """Get a channel layer by alias.

        Args:
            alias: The channel layer alias.

        Returns:
            The channel layer instance.

        Raises:
            KeyError: If the alias is not registered.
        """
        layer = self._layers.get(alias)
        if layer is None:
            raise KeyError(f"Channel layer '{alias}' not registered")
        return layer

    def __len__(self) -> int:
        """Get the number of registered channel layers.

        Returns:
            The number of registered channel layers.
        """
        return len(self._layers)


# Default global instance of the channel layer registry
channel_layers = ChannelLayerRegistry()


def get_channel_layer(alias: str) -> BaseChannelLayer | None:
    """
    Returns a channel layer by alias.
    """
    return channel_layers.get(alias)


def register_channel_layer(alias: str, layer: BaseChannelLayer) -> None:
    """
    Register a channel layer instance.

    Example:
        layer = create_redis_channel_layer("redis://localhost:6379")
        register_channel_layer("my_layer", layer)
    """
    channel_layers.register(alias, layer)


def unregister_channel_layer(alias: str) -> None:
    """
    Remove a channel layer from the registry.
    """
    channel_layers.unregister(alias)


def has_layers() -> bool:
    """
    Check if any channel layers are registered.

    Returns:
        True if channel layers are registered, False otherwise.
    """
    return len(channel_layers) > 0

