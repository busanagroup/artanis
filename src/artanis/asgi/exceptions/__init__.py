#!/usr/bin/env python
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

from starlette.responses import HTMLResponse

from artanis.asgi import types


async def bad_request(scope: types.Scope, receive: types.Receive, send: types.Send, exc: Exception):
    from .http_400 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=400)

async def unauthorized(scope: types.Scope, receive: types.Receive, send: types.Send, exc: Exception):
    from .http_401 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=401)

async def forbidden(scope: types.Scope, receive: types.Receive, send: types.Send, exc: Exception):
    from .http_403 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=403)

async def not_found(scope: types.Scope, receive: types.Receive, send: types.Send, exc: Exception):
    from .http_404 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=404)

async def method_not_allowed(scope: types.Scope, receive: types.Receive, send: types.Send, exc: Exception):
    from .http_405 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=405)

async def request_time_out(scope: types.Scope, receive: types.Receive, send: types.Send, exc: Exception):
    from .http_408 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=408)

async def server_error(scope: types.Scope, receive: types.Receive, send: types.Send, exc: Exception):
    from .http_500 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=500)

async def not_implemented(scope: types.Scope, receive: types.Receive, send: types.Send, exc: Exception):
    from .http_501 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=501)

async def bad_gateway(scope: types.Scope, receive: types.Receive, send: types.Send, exc: Exception):
    from .http_502 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=502)

async def service_unavailable(scope: types.Scope, receive: types.Receive, send: types.Send, exc: Exception):
    from .http_503 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=503)

async def gateway_timeout(scope: types.Scope, receive: types.Receive, send: types.Send, exc: Exception):
    from .http_504 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=504)

async def http_version_not_supported(scope: types.Scope, receive: types.Receive, send: types.Send, exc: Exception):
    from .http_505 import HTML_PAGE
    return HTMLResponse(content=HTML_PAGE, status_code=505)


exception_handlers = {
    400: bad_request,
    401: unauthorized,
    403: forbidden,
    404: not_found,
    405: method_not_allowed,
    500: server_error,
    501: not_implemented,
    502: bad_gateway,
    503: service_unavailable,
    504: gateway_timeout,
    505: http_version_not_supported,
}

__all__ = (exception_handlers,)
