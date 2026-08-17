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
__copyright__ = 'Copyright (c) 2025 Busana Apparel Group'

import uuid

from artanis.sqlentity import fields
from artanis.sqlentity.indexes import UniqueIndex
from artanis.sqlentity.sqlorm import Entity


class efmque(Entity):
    """
    Message Queue pool
    """

    mquepkid = fields.UUIDField(primary_key=True, default=uuid.uuid7, label='Queue ID')
    mquexchg = fields.CharField(max_length=32, label='Exchange Name')
    mquedata = fields.JSONField(label='Queue Data')
    mquestat = fields.IntField(label='Queue Status', index=True)
    mquetime = fields.DatetimeField (auto_now_add=True, label='Timestamp')

    class Meta:
        indexes = [
            UniqueIndex(fields=['mquexchg', 'mquepkid'])
        ]
