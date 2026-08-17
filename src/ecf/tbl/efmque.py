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

import datetime as dt
import uuid

from artanis.sqlentity import fields
from artanis.sqlentity.indexes import UniqueIndex
from artanis.sqlentity.sqlorm import Entity


class efmque(Entity):
    """
    Message Queue pool
    """

    mquepkid = fields.UUIDField(pk=True, label='Queue ID', null=False, generated=False)
    mquexchg = fields.CharField(max_length=48, label='Exchange Name')
    mquetype = fields.IntField(label='Queue Type', index=True)
    mquedata = fields.BinaryField(label='Queue Data')
    mquestat = fields.IntField(label='Queue Status', index=True)
    mquetime = fields.DatetimeField(auto_now_add=True, label='Timestamp')

    class Meta:
        indexes = [
            UniqueIndex(fields=['mquexchg', 'mquepkid'])
        ]

    @classmethod
    async def create_queue(cls, exchange: str, data: bytes, que_type: int = 0, status: int = 0):
        queue_id = uuid.uuid7()
        await cls.create(
            mquepkid=queue_id,
            mquexchg=exchange,
            mquetype=que_type,
            mquedata=data,
            mquestat=status,
            mquetime=dt.datetime.now()
        )
        return queue_id

    @classmethod
    async def get_queue_except(cls, queue_id: uuid.UUID, que_type: int = 0, status: int = 0):

        # select mquepkid from efmque
        #   where mquetype = :que_type
        #     and mquestat = :status
        #     and mquepkid <> :queue_id
        #   order by mquexchg, mquepkid

        queue_list = await cls.filter(
            mquetype=que_type,
            mquestat=status,
        ).exclude(
            mquepkid=queue_id
        ).order_by(
            'mquexchg, mquepkid'
        ).all().values_list('mquepkid', flat=True)
        return [uuid.UUID(q.queue_id) for q in queue_list]

    @classmethod
    async def update_status(cls, queue_id: uuid.UUID, status: int):
        await cls.filter(mquepkid=queue_id).update(mquestat=status)

    @classmethod
    async def delete_queue(cls, queue_id: uuid.UUID):
        await cls.filter(mquepkid=queue_id).delete()
