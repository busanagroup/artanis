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
from artanis.sqlentity.indexes import Index, UniqueIndex
from artanis.sqlentity.sqlorm import Entity


class cesinf(Entity):
    """
    User Connect
    """
    csyscono = fields.CharField(max_length=3, label='Company')
    csysdvno = fields.CharField(max_length=3, label='Division')
    csysmocd = fields.CharField(max_length=16, label='Module Code')
    csysctcd = fields.CharField(max_length=16, label='Constant Code')
    csysstky = fields.CharField(max_length=48, label='Key Value')
    csyssbky = fields.CharField(max_length=48, label='Sub Key Value')
    csysstnm = fields.CharField(max_length=48, label='Key Name')
    csyssbnm = fields.CharField(max_length=48, label='Sub Key Name')
    csystx24 = fields.CharField(max_length=24, label='Text 24')
    csystx48 = fields.CharField(max_length=48, label='Text 48')
    csyst161 = fields.CharField(max_length=16, label='Additional Text 16')
    csyst162 = fields.CharField(max_length=16, label='Additional Text 16')
    csyst163 = fields.CharField(max_length=16, label='Additional Text 16')
    csyst164 = fields.CharField(max_length=16, label='Additional Text 16')
    csyst241 = fields.CharField(max_length=24, label='Additional Text 24')
    csyst242 = fields.CharField(max_length=24, label='Additional Text 24')
    csyst243 = fields.CharField(max_length=24, label='Additional Text 24')
    csyst244 = fields.CharField(max_length=24, label='Additional Text 24')
    csyst481 = fields.CharField(max_length=48, label='Additional Text 48')
    csyst482 = fields.CharField(max_length=48, label='Additional Text 48')
    csyst483 = fields.CharField(max_length=48, label='Additional Text 48')
    csyst484 = fields.CharField(max_length=48, label='Additional Text 48')
    csysbol1 = fields.SmallIntField(label='Additional bool')
    csysbol2 = fields.SmallIntField(label='Additional bool')
    csysbol3 = fields.SmallIntField(label='Additional bool')
    csysbol4 = fields.SmallIntField(label='Additional bool')
    csysint1 = fields.IntField(label='Additional Value')
    csysint2 = fields.IntField(label='Additional Value')
    csysint3 = fields.IntField(label='Additional Value')
    csysint4 = fields.IntField(label='Additional Value')
    csyscur1 = fields.DecimalField(max_digits=11, decimal_places=6, label='Additional Value')
    csyscur2 = fields.DecimalField(max_digits=11, decimal_places=6, label='Additional Value')
    csyscur3 = fields.DecimalField(max_digits=11, decimal_places=6, label='Additional Value')
    csyscur4 = fields.DecimalField(max_digits=11, decimal_places=6, label='Additional Value')

    class Meta:
        indexes = [
            UniqueIndex(fields=('csyscono', 'csysdvno', 'csysmocd', 'csysctcd', 'csysstky', 'csyssbky')),
            Index(fields=('csysaudt', 'csysautm')),
        ]
