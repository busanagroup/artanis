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


from taskiq.exceptions import ResultBackendError, ResultGetError, TaskiqError


class TaskIQRedisError(TaskiqError):
    """Base error for all taskiq-redis exceptions."""


class DuplicateExpireTimeSelectedError(ResultBackendError, TaskIQRedisError):
    """Error if two lifetimes are selected."""

    __template__ = "Choose either result_ex_time or result_px_time."


class ExpireTimeMustBeMoreThanZeroError(ResultBackendError, TaskIQRedisError):
    """Error if two lifetimes are less or equal zero."""

    __template__ = (
        "You must select one expire time param and it must be more than zero."
    )


class ResultIsMissingError(TaskIQRedisError, ResultGetError):
    """Error if there is no result when trying to get it."""
