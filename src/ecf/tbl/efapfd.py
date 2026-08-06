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


class efapfd(Entity):
    """API Field status"""
    apifldob = fields.CharField(max_length=32, label='API Object')
    apifldfn = fields.CharField(max_length=32, label='Function')
    apifldnm = fields.CharField(max_length=32, label='Field')
    apifldds = fields.CharField(max_length=64, label='Description')
    apifldio = fields.IntField(label='Input/Output')
    apifldtp = fields.CharField(max_length=16, label='Type')
    apifldln = fields.IntField(label='Length')
    apifldpr = fields.IntField(label='Precision')
    apiflddc = fields.IntField(label='Decimal')
    apifldrq = fields.BooleanField(label='Required')

    class Meta:
        indexes = [
            UniqueIndex(fields=['apifldob', 'apifldfn', 'apifldnm'])
        ]
