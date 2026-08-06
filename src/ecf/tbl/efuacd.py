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


class efuacd(Entity):
    """
    Alternate User Division
    """
    efususid = fields.CharField(max_length=24, label='User ID')
    efuscono = fields.CharField(max_length=3, label='Comp. ID')
    efusdvno = fields.CharField(max_length=3, label='Division')
    efusfsnm = fields.CharField(max_length=48, label='First Name')
    efuslsnm = fields.CharField(max_length=48, label='Last Name')
    efusconm = fields.CharField(max_length=48, label='Comp. ID')
    efusdvnm = fields.CharField(max_length=48, label='Division')

    class Meta:
        indexes = [
            UniqueIndex(fields=['efususid', 'efuscono', 'efusdvno'])
        ]
