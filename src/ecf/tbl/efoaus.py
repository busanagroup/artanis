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


class efoaus(Entity):
    """
    Object Access Group Users
    """

    efougrcd = fields.CharField(max_length=8, label='Obj. Code')
    efouusid = fields.CharField(max_length=24, label='User ID')
    efougrnm = fields.CharField(max_length=24, label='Obj. Name')
    efoufsnm = fields.CharField(max_length=48, label='First Name')
    efoulsnm = fields.CharField(max_length=48, label='Last Name')

    class Meta:
        indexes = [
            UniqueIndex(fields=['efougrcd', 'efouusid'])
        ]
