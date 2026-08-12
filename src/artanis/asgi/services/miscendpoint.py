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
import typing as t

import pydantic

from artanis.asgi import schemas
from artanis.asgi.asgiendpoint import ASGIEndPoint, Descriptor, published
from artanis.asgi.auth.handler import AuthenticationHandler
from artanis.asgi.auth.validator import MiscAccessValidator
from artanis.asgi.schemas.response import DefaultResponse
from artanis.asgi.services.mvcendpoint import MVCEndpointDescriptor
from artanis.asgi.types import UserInfo
from artanis.config import Configuration
from artanis.exceptions import HTTPException
from ecf.res import MenuDefinition, ViewDefinition


class ActionDef(pydantic.BaseModel):
    service: str | None
    name: str | None


class ViewDef(ActionDef):
    type: str | None


DefinitionRequest = t.Annotated[schemas.Schema, schemas.SchemaMetadata(ActionDef)]
ViewDefinitionRequest = t.Annotated[schemas.Schema, schemas.SchemaMetadata(ViewDef)]


class MiscEndPoint(ASGIEndPoint):
    menu_def: MenuDefinition | None = None

    descriptor: Descriptor = MVCEndpointDescriptor
    base_path = "/misc"
    openapi_support = True
    access_validator = MiscAccessValidator()
    auth_handler = AuthenticationHandler(Configuration.get_default_instance(create_instance=False))

    @property
    def menu_definition(self) -> MenuDefinition:
        if self.menu_def is None:
            self.menu_def = MenuDefinition()
        return self.menu_def

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
            pollingInterval=5,
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
        return dict(
            status=0,
            data=self.menu_definition.get_menu_definition(default_def)
        )

    @published(path="/action-view/{action_name:str}")
    async def get_action_view(self, action_name: str) -> DefaultResponse:
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
        return dict(
            status=0,
            data=self.menu_definition.get_action_view(action_name))

    @published(path="/view", methods=["POST"])
    async def get_view(self, req: ViewDefinitionRequest) -> DefaultResponse:
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
        #             status:
        #                 0 :    Success
        #                 -1:    Server Failure
        #                 -2:    Validation Failure
        #                 -3:    Unauthorized Error
        #                 -4:    Timeout
        try:
            if not req:
                raise HTTPException(status_code=400, detail="Invalid request data")
            service = req.get('service')
            view_name = req.get('name')
            view_type = req.get('type')
            if view_type in [None, '']:
                view_type = 'grid'
            if view_name in [None, '']:
                view_name = f"{service}-{view_type}"
            definition = ViewDefinition()
            view = definition.get_viewdef(service, view_name)
            if not view or view['defkind'] != view_type:
                raise HTTPException(status_code=400, detail="Invalid request data")
            status = 0
            result = dict(status=status, data=view)
        except HTTPException as ex:
            status = -1
            result = dict(status=status, data=None)
        return result

    @published(path="/action", methods=["POST"])
    async def get_action(self, req: DefinitionRequest) -> DefaultResponse:
        """
        tags:
            - Miscelaneous
        title:
            Get action definition
        description:
            Returns action definition for this application
        responses:
            200:
                description:
                    Successful ping.
        """
        #             status:
        #                 0 :    Success
        #                 -1:    Server Failure
        #                 -2:    Validation Failure
        #                 -3:    Unauthorized Error
        #                 -4:    Timeout
        try:
            if not req:
                raise HTTPException(status_code=400, detail="Invalid request data")
            service = req.get('service')
            action_name = req.get('name')
            definition = ViewDefinition()
            item_def = definition.get_action(service, action_name)
            if not item_def:
                raise HTTPException(status_code=400, detail="Invalid request data")
            status = 0
            result = dict(status=status, data=item_def)
        except HTTPException as ex:
            status = -1
            result = dict(status=status, data=None)
        return result

    @published(path="/search-filter", methods=["POST"])
    async def get_search_filter(self, req: DefinitionRequest) -> DefaultResponse:
        """
        tags:
            - Miscelaneous
        title:
            Get search filter definition
        description:
            Returns search filter definition for this application
        responses:
            200:
                description:
                    Successful ping.
        """
        #             status:
        #                 0 :    Success
        #                 -1:    Server Failure
        #                 -2:    Validation Failure
        #                 -3:    Unauthorized Error
        #                 -4:    Timeout
        try:
            if not req:
                raise HTTPException(status_code=400, detail="Invalid request data")
            service = req.get('service')
            action_name = req.get('name')
            definition = ViewDefinition()
            item_def = definition.get_search_filter(service, action_name)
            if not item_def:
                raise HTTPException(status_code=400, detail="Invalid request data")
            status = 0
            result = dict(status=status, data=item_def)
        except HTTPException as ex:
            status = -1
            result = dict(status=status, data=None)
        return result
