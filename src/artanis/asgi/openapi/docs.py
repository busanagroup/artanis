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
from __future__ import annotations

import json
from typing import Any

from starlette.responses import HTMLResponse

from artanis.encoder import jsonable_encoder


def _html_safe_json(value: Any) -> str:
    """Serialize a value to JSON with HTML special characters escaped.

    This prevents injection when the JSON is embedded inside a <script> tag.
    """
    return (
        json.dumps(value)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )


swagger_ui_default_parameters: dict = {
    "dom_id": "#swagger-ui",
    "layout": "BaseLayout",
    "deepLinking": True,
    "showExtensions": True,
    "showCommonExtensions": True,
}


def get_swagger_ui_html(
        openapi_url: str,
        title: str,
        oauth2_redirect_url: str = None,
        init_oauth: dict = None,
        swagger_ui_parameters: dict = None
) -> HTMLResponse:
    current_swagger_ui_parameters = swagger_ui_default_parameters.copy()
    if swagger_ui_parameters:
        current_swagger_ui_parameters.update(swagger_ui_parameters)
    html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" type="text/css" href="./docs/static/swagger-ui.css" />
        <link rel="stylesheet" type="text/css" href="./docs/static/index.css" />
        <link rel="icon" type="image/png" href="./docs/static/favicon-32x32.png" sizes="32x32" />
        <link rel="icon" type="image/png" href="./docs/static/favicon-16x16.png" sizes="16x16" />                
        <title>{title}</title>
        </head>
        <body>
        <div id="swagger-ui">
        </div>
        <script src="./docs/static/swagger-ui-bundle.js" charset="UTF-8"> </script>
        <script src="./docs/static/swagger-ui-standalone-preset.js" charset="UTF-8"> </script>        
        <!-- `SwaggerUIBundle` is now available on the page -->
        <script>
        const ui = SwaggerUIBundle({{
            url: '{openapi_url}',
        """

    for key, value in current_swagger_ui_parameters.items():
        html += f"{_html_safe_json(key)}: {_html_safe_json(jsonable_encoder(value))},\n"

    if oauth2_redirect_url:
        html += f"oauth2RedirectUrl: window.location.origin + '{oauth2_redirect_url}',"

    html += """
        presets: [
            SwaggerUIBundle.presets.apis,
            SwaggerUIBundle.SwaggerUIStandalonePreset
            ],
        })"""

    if init_oauth:
        html += f"""
            ui.initOAuth({_html_safe_json(jsonable_encoder(init_oauth))})
            """

    html += """
        </script>
        </body>
        </html>
        """
    return HTMLResponse(html)


def get_swagger_ui_oauth2_redirect_html() -> HTMLResponse:
    """
    Generate the HTML response with the OAuth2 redirection for Swagger UI.

    You normally don't need to use or change this.
    """
    # copied from https://github.com/swagger-api/swagger-ui/blob/v4.14.0/dist/oauth2-redirect.html
    html = """
    <!doctype html>
    <html lang="en-US">
    <body>
    <script src="./docs/static/oauth2-redirect.js"></script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
