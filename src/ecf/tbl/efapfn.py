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


class efapfn(Entity):
    """API Object Function status"""
    apifncob = fields.CharField(max_length=32, label='API Object')
    apifncnm = fields.CharField(max_length=32, label='Function')
    apifncds = fields.CharField(max_length=64, label='Description')
    apifncst = fields.BooleanField(label='Status')
    apifnctp = fields.CharField(max_length=1, label='Function type')
    apifncsl = fields.BooleanField(label='Can Select')
    apifncin = fields.BooleanField(label='Can Insert')
    apifncup = fields.BooleanField(label='Can Update')
    apifncdl = fields.BooleanField(label='Can Delete')
    apifncex = fields.BooleanField(label='Can Ext')

    class Meta:
        indexes = [
            UniqueIndex(fields=['apifncob', 'apifncnm'])
        ]
