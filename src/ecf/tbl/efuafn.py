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


class efuafn(Entity, table=True):
    """User access API function"""
    uafusrnm : str = Field(String(24), label='User name', primary_key=True)
    uafobjnm : str = Field(String(32), label='API object name', primary_key=True)
    uaffncnm : str = Field(String(32), label='API function name', primary_key=True)
    uaffncsl : bool = Field(Boolean, label='Select')
    uaffncin : bool = Field(Boolean, label='Insert')
    uaffncup : bool = Field(Boolean, label='Update')
    uaffncdl : bool = Field(Boolean, label='Delete')
    uaffncex : bool = Field(Boolean, label='Extended functionality')
    uaffaudt : int = Field(Numeric(8, 0), label='Audit date')
    uaffautm : int = Field(Numeric(6, 0), label='Audit time')
    uaffauus : str = Field(String(24), label='Audit user')

    @classmethod
    async def check_api_func(cls, user_name: str, obj_name: str, func_name: str, access_type: str) -> bool:
        res = True
        ob = await cls.get_by(uafusrnm='*', uafobjnm='*', uaffncnm='*')
        if not ob:
            ob = await cls.get_by(uafusrnm=user_name, uafobjnm='*', uaffncnm='*')
            if not ob:
                ob = await cls.get_by(uafusrnm=user_name, uafobjnm=obj_name, uaffncnm='*')
                if not ob:
                    ob = await cls.get_by(uafusrnm=user_name, uafobjnm=obj_name, uaffncnm=func_name)
                    res = ob is not None
        if not res:
            return False
        check_access = {
            'S': ob.uaffncsl,
            'I': ob.uaffncin,
            'U': ob.uaffncup,
            'D': ob.uaffncdl,
            'X': ob.uaffncex,
        }
        return check_access[access_type.upper()] == 1
