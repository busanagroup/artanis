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

__author__ = 'Jaimy Azle'
__version__ = '2.0'
__copyright__ = 'Copyright (c) 2025 Busana Apparel Group'

from artanis.sqlentity import *


class efuaob(Entity):
    """User Access API Object"""
    uaousrnm = Field(String(24), label='User name', primary_key=True)
    uaoobjnm = Field(String(32), label='API Object name', primary_key=True)
    uaooaudt = Field(Numeric(8, 0), label='Audit date')
    uaooautm = Field(Numeric(6, 0), label='Audit time')
    uaooauus = Field(String(24), label='Audit user')

    @classmethod
    async def check_api_obj(cls, user_name: str, obj_name: str) -> bool:
        res = True
        ob = await cls.get_by(uaousrnm='*', uaoobjnm='*')
        if not ob:
            ob = await cls.get_by(uaousrnm=user_name, uaoobjnm='*')
            if not ob:
                ob = await cls.get_by(uaousrnm=user_name, uaoobjnm=obj_name)
                res = ob is not None
        return res
