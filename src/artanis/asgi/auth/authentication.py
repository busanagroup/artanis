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

from starlette.authentication import SimpleUser

if t.TYPE_CHECKING:
    from artanis.asgi import types
    from artanis.asgi.asgibase import BaseASGIService
    from artanis.asgi.http import Response


class ArtanisUser(SimpleUser):
    
    def __init__(self, username: str, payload: dict) -> None:
        super().__init__(username)
        self.payload = {}.update(payload)



class AuthenticationBackend:

    async def authenticate(self, sender, scope: "types.Scope",
                           receive: "types.Receive") -> "Response | BaseASGIService":
        raise NotImplementedError()  # pragma: no cover
