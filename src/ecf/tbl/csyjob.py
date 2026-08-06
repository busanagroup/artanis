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

from artanis.sqlentity import fields
from artanis.sqlentity.indexes import UniqueIndex
from artanis.sqlentity.sqlorm import Entity


class csyjob(Entity):
    """
    User Defined Job parameters
    """
    cjobcono = fields.CharField(max_length=3, label='Company')
    cjobdvno = fields.CharField(max_length=3, label='Division')
    cjobrqus = fields.CharField(max_length=24, label='Requested user')
    cjobctcd = fields.CharField(max_length=10, label='Constant Code')
    cjobstky = fields.CharField(max_length=16, label='Key Value')
    cjobt161 = fields.CharField(max_length=24, label='Value 16')
    cjobt162 = fields.CharField(max_length=24, label='Value 16')
    cjobt163 = fields.CharField(max_length=24, label='Value 16')
    cjobt164 = fields.CharField(max_length=24, label='Value 16')
    cjobt241 = fields.CharField(max_length=24, label='Value 24')
    cjobt242 = fields.CharField(max_length=24, label='Value 24')
    cjobt243 = fields.CharField(max_length=24, label='Value 24')
    cjobt244 = fields.CharField(max_length=24, label='Value 24')
    cjobt321 = fields.CharField(max_length=24, label='Value 32')
    cjobt322 = fields.CharField(max_length=24, label='Value 32')
    cjobt323 = fields.CharField(max_length=24, label='Value 32')
    cjobt324 = fields.CharField(max_length=24, label='Value 32')
    cjobt481 = fields.CharField(max_length=48, label='Value 48')
    cjobt482 = fields.CharField(max_length=48, label='Value 48')
    cjobt483 = fields.CharField(max_length=48, label='Value 48')
    cjobt484 = fields.CharField(max_length=48, label='Value 48')
    cjobt641 = fields.CharField(max_length=64, label='Value 64')
    cjobt642 = fields.CharField(max_length=64, label='Value 64')
    cjobt643 = fields.CharField(max_length=64, label='Value 64')
    cjobt644 = fields.CharField(max_length=64, label='Value 64')
    cjobint1 = fields.IntField(label='Int Value')
    cjobint2 = fields.IntField(label='Int Value')
    cjobint3 = fields.IntField(label='Int Value')
    cjobint4 = fields.IntField(label='Int Value')
    cjobcur1 = fields.DecimalField(max_digits=15, decimal_places=6, label='Curr Value')
    cjobcur2 = fields.DecimalField(max_digits=15, decimal_places=6, label='Curr Value')
    cjobcur3 = fields.DecimalField(max_digits=15, decimal_places=6, label='Curr Value')
    cjobcur4 = fields.DecimalField(max_digits=15, decimal_places=6, label='Curr Value')
    cjobjbid = fields.CharField(max_length=38, label='Job ID', unique=True)

    class Meta:
        indexes = [
            UniqueIndex(fields=['cjobcono', 'cjobdvno', 'cjobrqus', 'cjobctcd', 'cjobstky'])
        ]
