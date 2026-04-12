#
# Copyright (c) 2017 Busana Apparel Group. All rights reserved.
#
# This product and it's source code is protected by patents, copyright laws and
# international copyright treaties, as well as other intellectual property
# laws and treaties. The product is licensed, not sold.
#
# The source code and sample programs in this package or parts hereof
# as well as the documentation shall not be copied, modified or redistributed
# without permission, explicit or implied, of the author.
#

__author__ = 'widodo'
__version__ = '2.0'
__copyright__ = 'Copyright (c) 2017 Busana Apparel Group'

from artanis.sqlentity.sqlorm import *


class efmxob(Entity):
    """
    User Exception MVC Object 
    """
    umoxsrnm = Field(String(24), label='User name', primary_key=True)
    umoxbjnm = Field(String(32), label='Object Name', primary_key=True)
    umoxbjsl = Field(Integer, label='Access for select')
    umoxbjin = Field(Integer, label='Access for insert')
    umoxbjup = Field(Integer, label='Access for update')
    umoxbjdl = Field(Integer, label='Access for delete')
    umoxbjex = Field(Integer, label='Access for extended functionality')
    umoxaudt = Field(Numeric(8, 0), label='Audit date')
    umoxautm = Field(Numeric(6, 0), label='Audit time')
    umoxauus = Field(String(24), label='Audit user')

    @classmethod
    def check_access(cls, obj, acctp):
        # --- do we really need this ????
        chkaccess = {
            'S': obj.umoxbjsl,
            'I': obj.umoxbjin,
            'U': obj.umoxbjup,
            'D': obj.umoxbjdl,
            'X': obj.umoxbjex,
        }
        return chkaccess[acctp] == 0 if acctp in chkaccess else True

    @classmethod
    async def check_public_access(cls, objnm, acctp):
        obj = await cls.get_by(umoxsrnm='*', umoxbjnm='*')
        if not obj:
            obj = await cls.get_by(umoxsrnm='*', umoxbjnm=objnm)
        res = obj is None
        return res if res else cls.check_access(obj, acctp)

    @classmethod
    async def check_user_access(cls, usrnm, objnm, acctp):
        obj = await cls.get_by(umoxsrnm=usrnm, umoxbjnm=objnm)
        return obj is None

    @classmethod
    async def verify_user_access(cls, usrnm, objnm, acctp, check_access=True):
        obj = await cls.get_by(umoxsrnm='*', umoxbjnm='*')
        if not obj:
            obj = await cls.get_by(umoxsrnm=usrnm, umoxbjnm='*')
            if not obj:
                obj = await cls.get_by(umoxsrnm='*', umoxbjnm=objnm)
                if not obj:
                    obj = await cls.get_by(umoxsrnm=usrnm, umoxbjnm=objnm)

        res = obj is None
        ret_res = res if res else cls.check_access(obj, acctp)
        return res if not check_access else ret_res
