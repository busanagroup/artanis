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


class efumob(Entity):
    """User Access MVC Object"""
    umousrnm = fields.CharField(max_length=24, label='User name')
    umoobjnm = fields.CharField(max_length=32, label='Object Name')
    umoobjsl = fields.IntField(label='Access for select')
    umoobjin = fields.IntField(label='Access for insert')
    umoobjup = fields.IntField(label='Access for update')
    umoobjdl = fields.IntField(label='Access for delete')
    umoobjex = fields.IntField(label='Access for extended functionality')

    class Meta:
        indexes = [
            UniqueIndex(fields=['umousrnm', 'umoobjnm'])
        ]

    @classmethod
    def check_access(cls, obj, acctp):
        chkaccess = {
            'S': obj.umoobjsl,
            'I': obj.umoobjin,
            'U': obj.umoobjup,
            'D': obj.umoobjdl,
            'X': obj.umoobjex,
        }
        return chkaccess[acctp] == 1 if acctp in chkaccess else False

    @classmethod
    async def check_public_access(cls, objnm, acctp):
        res = True
        obj = await cls.get(umousrnm='*', umoobjnm='*')
        if not obj:
            obj = await cls.get(umousrnm='*', umoobjnm=objnm)
            res = obj is not None
        return res if not res else cls.check_access(obj, acctp)

    @classmethod
    async def check_user_access(cls, usrnm, objnm, acctp):
        res = True
        obj = await cls.get(umousrnm=usrnm, umoobjnm='*')
        if not obj:
            obj = await cls.get(umousrnm=usrnm, umoobjnm=objnm)
            res = obj is not None
        return res if not res else cls.check_access(obj, acctp)

    @classmethod
    async def verify_user_access(cls, usrnm, objnm, acctp, check_access=True):
        res = True
        obj = await cls.get(umousrnm='*', umoobjnm='*')
        if not obj:
            obj = await cls.get(umousrnm=usrnm, umoobjnm='*')
            if not obj:
                obj = await cls.get(umousrnm='*', umoobjnm=objnm)
                if not obj:
                    obj = await cls.get(umousrnm=usrnm, umoobjnm=objnm)
                    res = obj is not None
        ret_res = res if not res else cls.check_access(obj, acctp)
        return res if not check_access else ret_res
