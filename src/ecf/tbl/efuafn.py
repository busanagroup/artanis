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

from artanis.sqlentity import fields
from artanis.sqlentity.indexes import UniqueIndex
from artanis.sqlentity.sqlorm import Entity


class efuafn(Entity):
    """User access API function"""
    uafusrnm = fields.CharField(max_length=24, label='User name')
    uafobjnm = fields.CharField(max_length=32, label='API object name')
    uaffncnm = fields.CharField(max_length=32, label='API function name')
    uaffncsl = fields.BooleanField(label='Select')
    uaffncin = fields.BooleanField(label='Insert')
    uaffncup = fields.BooleanField(label='Update')
    uaffncdl = fields.BooleanField(label='Delete')
    uaffncex = fields.BooleanField(label='Extended functionality')

    class Meta:
        indexes = [
            UniqueIndex(fields=['uafusrnm', 'uafobjnm', 'uaffncnm'])
        ]

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
