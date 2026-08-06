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
from artanis.sqlentity.indexes import Index
from artanis.sqlentity.sqlorm import Entity


class efusrs(Entity):
    """
    User list
    """
    efususid = fields.CharField(max_length=24, label='User ID', unique=True)
    efusustp = fields.CharField(max_length=3, label='User Type', index=True)
    efuspswd = fields.CharField(max_length=64, label='Password')
    efusfsnm = fields.CharField(max_length=48, label='First Name')
    efuslsnm = fields.CharField(max_length=48, label='Last Name')
    efusemad = fields.CharField(max_length=64, label='Email Addr')
    efusdesc = fields.CharField(max_length=64, label='Description')
    efuscono = fields.CharField(max_length=3, label='Comp. ID')
    efusconm = fields.CharField(max_length=48, label='Comp. Name')
    efusdvno = fields.CharField(max_length=3, label='Division ID')
    efusdvnm = fields.CharField(max_length=48, label='Division Name')
    efusapst = fields.IntField(label='API Enabled')
    efusapky = fields.CharField(max_length=64, label='API Hash Value')
    efusstat = fields.IntField(label='Status')

    class Meta:
        indexes = [
            Index(fields=('efusustp', 'efususid')),
        ]
