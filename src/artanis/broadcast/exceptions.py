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


class InvalidChannelLayerError(ValueError):
    """
    Raised when a channel layer is configured incorrectly.
    """

    pass


class AcceptConnection(Exception):
    """
    Raised during a websocket.connect (or other supported connection) handler
    to accept the connection.
    """

    pass


class DenyConnection(Exception):
    """
    Raised during a websocket.connect (or other supported connection) handler
    to deny the connection.
    """

    pass


class ChannelFull(Exception):
    """
    Raised when a channel cannot be sent to as it is over capacity.
    """

    pass


class MessageTooLarge(Exception):
    """
    Raised when a message cannot be sent as it's too big.
    """

    pass


class StopConsumer(Exception):
    """
    Raised when a consumer wants to stop and close down its application instance.
    """

    pass
