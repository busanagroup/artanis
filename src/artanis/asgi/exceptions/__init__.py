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

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse

async def bad_request(request: Request, exc: HTTPException):
    from .http_400 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=exc.status_code)

async def unauthorized(request: Request, exc: HTTPException):
    from .http_401 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=exc.status_code)

async def forbidden(request: Request, exc: HTTPException):
    from .http_403 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=exc.status_code)

async def not_found(request: Request, exc: HTTPException):
    from .http_404 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=exc.status_code)

async def method_not_allowed(request: Request, exc: HTTPException):
    from .http_405 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=exc.status_code)

async def request_time_out(request: Request, exc: HTTPException):
    from .http_408 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=exc.status_code)

async def server_error(request: Request, exc: HTTPException):
    from .http_500 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=exc.status_code)

async def not_implemented(request: Request, exc: HTTPException):
    from .http_501 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=exc.status_code)

async def bad_gateway(request: Request, exc: HTTPException):
    from .http_502 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=exc.status_code)

async def service_unavailable(request: Request, exc: HTTPException):
    from .http_503 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=exc.status_code)

async def gateway_timeout(request: Request, exc: HTTPException):
    from .http_504 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=exc.status_code)

async def http_version_not_supported(request: Request, exc: HTTPException):
    from .http_505 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=exc.status_code)


exception_handlers = {
    400: bad_request,
    401: unauthorized,
    403: forbidden,
    404: not_found,
    500: server_error,
    501: not_implemented,
    502: bad_gateway,
    503: service_unavailable,
    504: gateway_timeout,
    505: http_version_not_supported,
}

__all__ = (exception_handlers,)
