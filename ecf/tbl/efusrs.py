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

from ecf.core.ecfutils import get_hash_key


class efusrs(Entity):
    """
    User list
    """
    efususid = Field(String(24), label='User ID', primary_key=True)
    efusustp = Field(String(3), label='User Type', index=True)
    efuspswd = Field(String(64), label='Password')
    efusfsnm = Field(String(48), label='First Name')
    efuslsnm = Field(String(48), label='Last Name')
    efusemad = Field(String(64), label='Email Addr')
    efusdesc = Field(String(64), label='Description')
    efuscono = Field(String(3), label='Comp. ID', index=True)
    efusconm = Field(String(24), label='Comp. ID')
    efusdvno = Field(String(3), label='Division', index=True)
    efusdvnm = Field(String(24), label='Division')
    efusstat = Field(Integer, label='Status')
    efusaudt = Field(Numeric(8, 0), label='Audit date')
    efusautm = Field(Numeric(6, 0), label='Audit time')
    efusauus = Field(String(24), label='Audit user')

    @classmethod
    async def get_user_password(cls, user_name: str):
        obj = await cls.get(user_name)
        return [obj.efuspswd, obj.efusstat, obj.efusfsnm, obj.efuslsnm, obj.efusemad] \
            if obj and (obj.efusstat != 0) else None

    @classmethod
    async def check_user_auth(cls, user_name: str, passwd: str):
        password = get_hash_key(passwd)
        ob = await cls.get_by(efususid=user_name, efuspswd=password, efusstat=1, efusustp='USR')
        return ob is not None

    @classmethod
    async def is_user_active(cls, user_name: str):
        obj = await cls.get_user_password(user_name)
        return (obj is not None) and (obj[1] == 1)

    @classmethod
    async def change_user_password(cls, user_name: str, old_passwd: str, new_passwd: str, auto_commit: bool = True):
        password = get_hash_key(old_passwd)
        obj = await cls.get_by(efususid=user_name, efuspswd=password)
        if obj:
            password = get_hash_key(new_passwd)
            obj.efuspswd = password
            session = Session()
            if (not session.is_active) and auto_commit:
                session.begin()
            try:
                session.add(obj)
                if auto_commit:
                    await session.commit()
            except:
                if auto_commit:
                    await session.rollback()
                raise
        else:
            raise Exception('Username could not be found or password does not match')
