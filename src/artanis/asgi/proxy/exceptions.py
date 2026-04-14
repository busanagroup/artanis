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

class BadTargetUrlError(ValueError):
    """Bad target url of forward http proxy."""


class ReverseProxyServerError(RuntimeError):
    """502 reverse proxy server error error."""


class BaseURLError(ValueError):
    """Invalid URL."""


class RejectedProxyRequestError(RuntimeError):
    """Should be raised when reject proxy request."""


class UnsupportedHttpVersionError(RuntimeError):
    """Unsupported http version."""
