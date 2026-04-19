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


class ECFError(Exception):
    """Generic ECF error class."""


class ECFServiceError(ECFError):
    """Generic ECF Service exception"""


class ECFAPIError(ECFServiceError):
    """Generic API error class."""


class ECFAPIUndefinedFunctionError(ECFAPIError):
    """Raised when attempt to call an undefined API function"""


class ECFAPIServiceNotAvailable(ECFAPIError):
    """API Service not available error class."""


class ECFINTServiceError(ECFServiceError):
    """Generic INT Service error class."""


class ECFINTServiceNotAvailable(ECFINTServiceError):
    """INT Service not available error class."""


class ECFDMServiceError(ECFServiceError):
    """Generic DataModule Service error class."""


class ECFDMServiceNotAvailable(ECFDMServiceError):
    """DataModule Service not available error class."""


class ECFRPCServiceError(ECFServiceError):
    """Generic RPC Service error class."""


class ECFRPCServiceNotAvailable(ECFDMServiceError):
    """RPCService not available error class."""


class ECFMVCServiceError(ECFServiceError):
    """Generic MVC Service error class."""


class ECFMVCServiceNotAvailable(ECFMVCServiceError):
    """MVC Service not available error class."""


class ECFRPTServiceError(ECFServiceError):
    """Generic Reporting Service error class."""


class ECFRPTServiceNotAvailable(ECFRPTServiceError):
    """Reporting Service not available error class."""


class ECFJOBServiceError(ECFServiceError):
    """Generic JOB Service error class."""


class ECFJOBServiceNotAvailable(ECFJOBServiceError):
    """JOB Service not available error class."""


class ECFBOServiceError(ECFServiceError):
    """Generic Business object service error class."""


class ECFBOServiceNotAvailable(ECFBOServiceError):
    """Business Object Service not available error class."""


class ECFImproperlyConfigured(ECFBOServiceError):
    """Server is somehow improperly configured"""


class ECFBusinessServiceError(ECFBOServiceError):
    """Generic Business Service Error"""


class ECFMasterDataError(ECFBusinessServiceError):
    """Master data could not be found"""


class ECFDirectCallServiceError(ECFBusinessServiceError):
    """Direct call service error"""

    def __init__(self, sender, *args):
        if isinstance(sender, object):
            super(ECFDirectCallServiceError, self).__init__(
                "Direct call service for %s is not allowed" % sender.__class__.__name__)
        else:
            super(ECFDirectCallServiceError, self).__init__(*args)


class ECFCompanyNotConfiguredError(ECFBusinessServiceError):
    """Company has not been configured properly"""


class ECFDivisionNotConfiguredError(ECFBusinessServiceError):
    """Company Division has not been configured properly"""


class ECFNotifyServiceError(ECFServiceError):
    """Generic Notification service error class."""


class ECFNotifyServiceNotAvailable(ECFNotifyServiceError):
    """Notification Service not available error class."""


class ECFNotifyEventNotAvailable(ECFNotifyServiceError):
    """Notification event not available error class."""


class ECFNotifyEventFuncNotCallable(ECFNotifyServiceError):
    """Notification event function not callable error class."""
