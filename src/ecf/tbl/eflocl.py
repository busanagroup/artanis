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


class eflocl(Entity):
    """
    Locale message
    """
    eflclccd = fields.CharField(max_length=16, label='Language ID')
    eflcmdcd = fields.CharField(max_length=32, label='Module')
    eflcmsid = fields.CharField(max_length=32, label='Hash ID')
    eflcmdtp = fields.IntField(label='Module type')
    eflcmssr = fields.CharField(max_length=250, label='Message')
    eflcmsls = fields.CharField(max_length=250, label='Translation')
    eflcaudt = fields.DecimalField(max_digits=8, decimal_places=0, label='Audit user')
    eflcautm = fields.DecimalField(max_digits=6, decimal_places=0, label='Audit time')
    eflcauus = fields.CharField(max_length=24, label='Audit user')

    class Meta:
        indexes = [
            UniqueIndex(fields=['eflclccd', 'eflcmdcd', 'eflcmsid']),
        ]
