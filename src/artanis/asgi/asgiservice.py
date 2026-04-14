#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Busana Apparel Group. All rights reserved.
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
import asyncio
import logging
import uuid

from artanis.asgi.asgibase import BaseASGIService
from artanis.asgi.auth import AccessTokenComponent, RefreshTokenComponent
from artanis.asgi.middlewares import Middleware, CORSMiddleware, GZipMiddleware
from artanis.config import Configuration
from artanis.entrypoint import artanis_monitor, artanis_startup, artanis_shutdown

logger = logging.getLogger(__name__)

__all__ = ["ASGIService"]


class ASGIService(BaseASGIService):

    def __init__(
            self,
            config: Configuration | None = None,
            debug: bool = False,
            parent: ASGIService | None = None,
            schema_library: str | None = "pydantic",
    ):
        config: Configuration = config or Configuration.get_default_instance(create_instance=False)
        app_name = config.get_property_value(Configuration.ARTANIS_APP_NAME, '')
        openapi = {
            "info": {
                "title": app_name,
                "version": "0.1.0",
                "summary": f"{app_name} application",
                "description": "The future is ours",
            },
        }
        super().__init__(
            config=config,
            debug=debug,
            openapi=openapi,
            schema_library=schema_library,
            parent=parent
        )

    def configure_lifespan(self, config):
        async def internal_scheduler():
            try:
                while True:
                    await asyncio.sleep(60)
                    await artanis_monitor(config)
            except asyncio.CancelledError:
                pass

        async def process_startup():
            loop = asyncio.get_event_loop()
            loop.create_task(internal_scheduler())
            await artanis_startup(config)
            await self.start()

        async def process_shutdown():
            await self.stop()
            await artanis_shutdown(config)

        self.add_event_handler("startup", process_startup)
        self.add_event_handler("shutdown", process_shutdown)
        self.events.startup += [mod.on_startup for mod in self.modules.values()]
        self.events.shutdown += [mod.on_shutdown for mod in self.modules.values()]

    def configure_middlewares(self, config):
        cors = config.get_property_value(config.ARTANIS_SECURITY_CORS_ORIGINS, '')
        self.add_middleware(Middleware(
            GZipMiddleware,
            minimum_size=2048,
            compresslevel=7,
        ))
        self.add_middleware(Middleware(
            CORSMiddleware,
            allow_origins=cors.split(','),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ))

    def configure_components(self, config):
        jwt_secret = config.get_property_value(config.JWT_SECRET_KEY, str(uuid.UUID(int=0)))
        components = [
            AccessTokenComponent(
                jwt_secret.encode(),
                header_prefix=config.get_property_value(config.JWT_HEADER_PREFIX),
                header_key=config.get_property_value(config.JWT_ACCESS_COOKIE_KEY),
                cookie_key=config.get_property_value(config.JWT_ACCESS_COOKIE_KEY)
            ),
            RefreshTokenComponent(
                jwt_secret.encode(),
                header_prefix=config.get_property_value(Configuration.JWT_HEADER_PREFIX),
                header_key=config.get_property_value(Configuration.JWT_REFRESH_COOKIE_KEY),
                cookie_key=config.get_property_value(Configuration.JWT_REFRESH_COOKIE_KEY)
            )
        ]
        self.add_component_set(components)

