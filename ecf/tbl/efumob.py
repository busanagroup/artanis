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

from artanis.sqlentity.entity import *


class efumob(Entity):
    """User Access MVC Object"""
    umousrnm = Field(String(24), label='User name', primary_key=True)
    umoobjnm = Field(String(32), label='Object Name', primary_key=True)
    umoobjsl = Field(Integer, label='Access for select')
    umoobjin = Field(Integer, label='Access for insert')
    umoobjup = Field(Integer, label='Access for update')
    umoobjdl = Field(Integer, label='Access for delete')
    umoobjex = Field(Integer, label='Access for extended functionality')
    umooaudt = Field(Numeric(8, 0), label='Audit date')
    umooautm = Field(Numeric(6, 0), label='Audit time')
    umooauus = Field(String(24), label='Audit user')

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
        obj = await cls.get_by(umousrnm='*', umoobjnm='*')
        if not obj:
            obj = await cls.get_by(umousrnm='*', umoobjnm=objnm)
            res = obj is not None
        return res if not res else cls.check_access(obj, acctp)

    @classmethod
    async def check_user_access(cls, usrnm, objnm, acctp):
        res = True
        obj = await cls.get_by(umousrnm=usrnm, umoobjnm='*')
        if not obj:
            obj = await cls.get_by(umousrnm=usrnm, umoobjnm=objnm)
            res = obj is not None
        return res if not res else cls.check_access(obj, acctp)

    @classmethod
    async def verify_user_access(cls, usrnm, objnm, acctp, check_access=True):
        res = True
        obj = await cls.get_by(umousrnm='*', umoobjnm='*')
        if not obj:
            obj = await cls.get_by(umousrnm=usrnm, umoobjnm='*')
            if not obj:
                obj = await cls.get_by(umousrnm='*', umoobjnm=objnm)
                if not obj:
                    obj = await cls.get_by(umousrnm=usrnm, umoobjnm=objnm)
                    res = obj is not None
        ret_res = res if not res else cls.check_access(obj, acctp)
        return res if not check_access else ret_res



