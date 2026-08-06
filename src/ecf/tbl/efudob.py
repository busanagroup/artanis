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

__author__ = 'jaimy'
__version__ = '2.0'
__copyright__ = 'Copyright (c) 2015 Busana Apparel Group'

from artanis.sqlentity import fields
from artanis.sqlentity.indexes import UniqueIndex
from artanis.sqlentity.sqlorm import Entity


class efudob(Entity):
    """
    User Access DataModule Object
    """

    udmusrnm = fields.CharField(max_length=24, label='User name')
    udmobjnm = fields.CharField(max_length=32, label='Object Name')
    udmobjsl = fields.IntField(label='Access for select')
    udmobjin = fields.IntField(label='Access for insert')
    udmobjup = fields.IntField(label='Access for update')
    udmobjdl = fields.IntField(label='Access for delete')

    class Meta:
        indexes = [
            UniqueIndex(fields=['udmusrnm', 'udmobjnm'])
        ]

    @classmethod
    def check_access(cls, obj: typing.Any, access_type: str):
        chkaccess = {
            'S': obj.udmobjsl,
            'I': obj.udmobjin,
            'U': obj.udmobjup,
            'D': obj.udmobjdl,
        }
        return chkaccess[access_type] == 1 if access_type in chkaccess else False

    @classmethod
    async def check_public_access(cls, obj_name: str, access_type: str):
        res = True
        obj = await cls.get_by(udmusrnm='*', udmobjnm='*')
        if not obj:
            obj = await cls.get_by(udmusrnm='*', udmobjnm=obj_name)
            res = obj is not None
        return res if not res else cls.check_access(obj, access_type)

    @classmethod
    async def check_user_access(cls, user_name: str, obj_name: str, access_type: str):
        res = True
        obj = await cls.get_by(udmusrnm=user_name, udmobjnm='*')
        if not obj:
            obj = cls.get_by(udmusrnm=user_name, udmobjnm=obj_name)
            res = obj is not None
        return res if not res else cls.check_access(obj, access_type)

    @classmethod
    async def verify_user_access(cls, user_name: str, obj_name: str, access_type: str,
                                 should_check_access: bool = True):
        res = True
        obj = await cls.get_by(udmusrnm='*', udmobjnm='*')
        if not obj:
            obj = await cls.get_by(udmusrnm=user_name, udmobjnm='*')
            if not obj:
                obj = await cls.get_by(udmusrnm='*', udmobjnm=obj_name)
                if not obj:
                    obj = await cls.get_by(udmusrnm=user_name, udmobjnm=obj_name)
                    res = obj is not None

        ret_res = res if not res else cls.check_access(obj, access_type)
        return res if not should_check_access else ret_res
