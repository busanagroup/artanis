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

__author__ = 'Jaimy'
__version__ = '2.0'
__copyright__ = 'Copyright (c) 2026 Busana Apparel Group'

from artanis.sqlentity import fields
from artanis.sqlentity.indexes import Index
from artanis.sqlentity.sqlorm import Entity
from ecf.core.ecfutils import get_hash_key


class efusrs(Entity):
    """
    User list
    """
    efususid = fields.CharField(max_length=24, label='User ID', unique=True)
    efusustp = fields.CharField(max_length=3, label='User Type', index=True)
    efuspswd = fields.CharField(max_length=64, label='Password')
    efusfsnm = fields.CharField(max_length=48, label='First Name')
    efuslsnm = fields.CharField(max_length=48, label='Last Name')
    efusemad = fields.CharField(max_length=64, label='Email Addr')
    efusdesc = fields.CharField(max_length=64, label='Description')
    efuscono = fields.CharField(max_length=3, label='Comp. ID')
    efusconm = fields.CharField(max_length=48, label='Comp. Name')
    efusdvno = fields.CharField(max_length=3, label='Division ID')
    efusdvnm = fields.CharField(max_length=48, label='Division Name')
    efusapst = fields.IntField(label='API Enabled')
    efusapky = fields.CharField(max_length=64, label='API Hash Value')
    efusstat = fields.IntField(label='Status')

    class Meta:
        indexes = [
            Index(fields=('efusustp', 'efususid')),
        ]

    @classmethod
    async def get_user_password(cls, user_name: str):
        obj = await cls.get_or_none(efususid=user_name)
        return [obj.efuspswd, obj.efusstat, obj.efusfsnm, obj.efuslsnm, obj.efusemad] \
            if obj and (obj.efusstat != 0) else None

    @classmethod
    async def check_user_auth(cls, user_name: str, passwd: str):
        password = get_hash_key(passwd)
        ob = await cls.get_or_none(efususid=user_name, efuspswd=password, efusstat=1, efusustp='USR')
        return ob is not None

    @classmethod
    async def is_user_active(cls, user_name: str):
        obj = await cls.get_user_password(user_name)
        return (obj is not None) and (obj[1] == 1)

    @classmethod
    async def change_user_password(cls, user_name: str, old_passwd: str, new_passwd: str, auto_commit: bool = True):
        password = get_hash_key(old_passwd)
        obj = await cls.get_or_none(efususid=user_name, efuspswd=password)
        if obj:
            password = get_hash_key(new_passwd)
            obj.efuspswd = password
            await obj.save(force_update=auto_commit)
        else:
            raise Exception('Username could not be found or password does not match')

    @classmethod
    async def get_user_api_key(cls, api_key: str):
        hash_value = get_hash_key(api_key)
        obj = await cls.get_or_none(efusapky=hash_value, efusstat=1, efusapst=1, efusustp='USR')
        return [obj.efususid, obj.efusfsnm, obj.efuslsnm, obj.efusemad, obj.efuscono, obj.efusconm,
                obj.efusdvno, obj.efusdvnm] if obj else None

    @classmethod
    async def save_api_key(
            cls,
            user_name: str,
            passwd: str,
            api_key: str,
            replace_existing: bool = False,
            auto_commit: bool = True
    ) -> bool:
        retval: bool = False
        password = get_hash_key(passwd)
        objs = await cls.get_or_none(efususid=user_name, efuspswd=password, efusstat=1, efusustp='USR')
        # check whether api access were allowed
        for ob in objs:
            if ob.efusapst == 1 and (not replace_existing or not ob.efusapky):
                api_hash = get_hash_key(api_key)
                ob.efusapky = api_hash
                await ob.save(force_update=auto_commit)
                retval = True
                break
        return retval

    @classmethod
    async def get_user_info(cls, user_name: str | None):
        if not user_name:
            return None
        obj = await cls.get_or_none(efususid=user_name)
        return [obj.efususid, obj.efusfsnm, obj.efuslsnm, obj.efusemad, obj.efuscono, obj.efusconm,
                obj.efusdvno, obj.efusdvnm] if obj and (obj.efusstat != 0) else None
