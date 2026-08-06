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


class efsyvr(Entity):
    """
    System Parameter Param
    """
    efsycono = fields.CharField(max_length=3, label='Comp ID')
    efsyusid = fields.CharField(max_length=24, label='User ID')
    efsypgid = fields.CharField(max_length=24, label='Program')
    efsyvrid = fields.CharField(max_length=24, label='Var')
    efsyvrv0 = fields.CharField(max_length=48, label='Value 1')
    efsyvrv1 = fields.CharField(max_length=48, label='Value 2')
    efsyvrv2 = fields.CharField(max_length=48, label='Value 3')
    efsyvrv3 = fields.CharField(max_length=48, label='Value 4')
    efsyvrv4 = fields.CharField(max_length=48, label='Value 5')
    efsyvrv5 = fields.CharField(max_length=48, label='Value 6')
    efsyvrv6 = fields.CharField(max_length=48, label='Value 7')
    efsyvrv7 = fields.CharField(max_length=48, label='Value 8')
    efsyvrv8 = fields.CharField(max_length=48, label='Value 9')
    efsyvrv9 = fields.CharField(max_length=48, label='Value 10')

    class Meta:
        indexes = [
            UniqueIndex(fields=['efsycono', 'efsyusid', 'efsypgid', 'efsyvrid'])
        ]
