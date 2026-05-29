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
from artanis.asgi.asgiendpoint import ASGIEndPoint, Descriptor, published
from artanis.asgi.auth.handler import AuthenticationHandler
from artanis.asgi.auth.validator import MiscAccessValidator
from artanis.asgi.services.mvcendpoint import MVCDescriptor
from artanis.asgi.types import UserInfo
from artanis.config import Configuration
from ecf.res import MenuDefinition


class MiscEndPoint(ASGIEndPoint):
    descriptor: Descriptor = MVCDescriptor
    base_path = "/misc"
    openapi_support = True
    access_validator = MiscAccessValidator()
    auth_handler = AuthenticationHandler(Configuration.get_default_instance(create_instance=False))

    @published(path="/info")
    async def get_app_info(self, userInfo: UserInfo):
        """
        tags:
            - Miscelaneous
        title:
            Get Application Info
        description:
            Returns various information about the application
        responses:
            200:
                description:
                    Successful ping.
        """
        config = self.get_configuration()
        feature = dict()
        view = dict(
            allowCustomization=False,
            form=dict(checkVersion=False),
            grid=dict(selectin=None),
            advancedSearch=dict(
                exportFull=True,
                share=True,
            ),
            singleTab=False,
            maxTabs=5,
        )
        application = dict(
            copyright=f"Copyright (c) 2026 {config.get_property_value(config.ARTANIS_CMP_NAME)}. All Rights Reserved",
            author="Jaimy & Garnes",
            aopVersion=config.get_property_value(config.ARTANIS_APP_VERSION),
            pollingInterval= 5,
            signIn=dict(
                footer="",
                title="<h3>Welcome to the Artanis</h3>",
            ),
            name=config.get_property_value(config.ARTANIS_APP_NAME),
            theme="auto",
            swaggerUI=dict(
                enabled=True,
                allowTryItOut=False,
            ),
            lang="en-US",
        )
        fullname = (userInfo.first_name + ' ' + userInfo.last_name) if userInfo.last_name else userInfo.first_name
        result = dict(
            feature=feature,
            view=view,
            application=application,
            api=dict(
                pagination=dict(
                    maxPerPage=1000,
                    defaultPerPage=100,
                )
            ),
            data=dict(
                upload=dict(
                    maxSize=5,
                )
            ),
            authentication=dict(
                callbackUrl="/auth/callback"
            ),
            user=dict(
                name=fullname,
                action=None,
                theme=None,
                id=userInfo.username,
                lang="en-US",
                nameField="name",
                singleTab=False,
                navigator=None,
                login=userInfo.username,
            )
        )
        return result

    @published(path="/menu")
    async def get_menu(self, user: UserInfo):
        """
        tags:
            - Miscelaneous
        title:
            Get Application Menu
        description:
            Returns menu definition for this application
        responses:
            200:
                description:
                    Successful ping.
        """
        default_def = await self.auth_handler.get_user_menudef(user.username)
        menu_def = MenuDefinition()
        return menu_def.get_menu_definition(default_def)
