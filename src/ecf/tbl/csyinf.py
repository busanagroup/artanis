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


class csyinf(Entity):
    """
    General System Information Container
    """

    cinfcono = fields.CharField(max_length=3, label='Company')
    cinfdvno = fields.CharField(max_length=3, label='Division')
    cinfctcd = fields.CharField(max_length=16, label='Constant Code')
    cinfstky = fields.CharField(max_length=48, label='Key Value')
    cinfsbky = fields.CharField(max_length=48, label='Sub Key Value')
    cinfscky = fields.CharField(max_length=48, label='Linked key Value', index=True)
    cinftx24 = fields.CharField(max_length=24, label='Name')
    cinftx48 = fields.CharField(max_length=48, label='Description')
    cinft241 = fields.CharField(max_length=24, label='Additional Value')
    cinft242 = fields.CharField(max_length=24, label='Additional Value')
    cinft243 = fields.CharField(max_length=24, label='Additional Value')
    cinft244 = fields.CharField(max_length=24, label='Additional Value')
    cinft481 = fields.CharField(max_length=48, label='Additional Value')
    cinft482 = fields.CharField(max_length=48, label='Additional Value')
    cinft483 = fields.CharField(max_length=48, label='Additional Value')
    cinft484 = fields.CharField(max_length=48, label='Additional Value')
    cinft641 = fields.CharField(max_length=64, label='Additional Value')
    cinft642 = fields.CharField(max_length=64, label='Additional Value')
    cinft643 = fields.CharField(max_length=64, label='Additional Value')
    cinft644 = fields.CharField(max_length=64, label='Additional Value')
    cinfint1 = fields.IntField(label='Additional Value')
    cinfint2 = fields.IntField(label='Additional Value')
    cinfint3 = fields.IntField(label='Additional Value')
    cinfint4 = fields.IntField(label='Additional Value')
    cinfcur1 = fields.DecimalField(max_digits=15, decimal_places=2, label='Additional Value')
    cinfcur2 = fields.DecimalField(max_digits=15, decimal_places=2, label='Additional Value')
    cinfcur3 = fields.DecimalField(max_digits=15, decimal_places=2, label='Additional Value')
    cinfcur4 = fields.DecimalField(max_digits=15, decimal_places=2, label='Additional Value')
    cinfdat1 = fields.DecimalField(max_digits=8, decimal_places=0, label='Additional Value')
    cinfdat2 = fields.DecimalField(max_digits=8, decimal_places=0, label='Additional Value')
    cinfdat3 = fields.DecimalField(max_digits=8, decimal_places=0, label='Additional Value')
    cinfdat4 = fields.DecimalField(max_digits=8, decimal_places=0, label='Additional Value')
    cinftim1 = fields.DecimalField(max_digits=6, decimal_places=0, label='Additional Value')
    cinftim2 = fields.DecimalField(max_digits=6, decimal_places=0, label='Additional Value')
    cinftim3 = fields.DecimalField(max_digits=6, decimal_places=0, label='Additional Value')
    cinftim4 = fields.DecimalField(max_digits=6, decimal_places=0, label='Additional Value')
    cinfist1 = fields.IntField(label='Informational Status')
    cinfist2 = fields.IntField(label='Informational Status')
    cinfist3 = fields.IntField(label='Informational Status')
    cinfist4 = fields.IntField(label='Informational Status')

    class Meta:
        indexes = [
            UniqueIndex(fields=['cinfcono', 'cinfdvno', 'cinfctcd', 'cinfstky', 'cinfsbky'])
        ]
