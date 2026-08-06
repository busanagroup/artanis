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


class efugrp(Entity):
    """
    User group
    """
    efuggrid = fields.CharField(max_length=24, label='Group ID')
    efugusid = fields.CharField(max_length=24, label='User ID')
    efugfsnm = fields.CharField(max_length=48, label='First name')
    efuglsnm = fields.CharField(max_length=48, label='Last name')

    class Meta:
        indexes = [
            UniqueIndex(fields=['efuggrid', 'efugusid'])
        ]

    @classmethod
    async def get_user_group(cls, user_name):
        user_name = '' if user_name is None else user_name
        retgrp = [user_name]
        curr_idx = 0
        while curr_idx < len(retgrp):
            next_grp = retgrp[curr_idx]
            objs = await cls.get_all(efugusid=next_grp)
            grps = [ob.efuggrid for ob in objs if ob.efuggrid not in retgrp]
            if len(grps) > 0:
                retgrp.extend(grps)
            curr_idx += 1
        return retgrp if len(retgrp) > 0 else None
