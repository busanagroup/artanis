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


class cmpdiv(Entity):
    """
    Company division
    """

    cmdvcono = fields.CharField(max_length=3, nullable=True, label='Company')
    cmdvdvno = fields.CharField(max_length=3, nullable=True, label='Division')
    cmdvconm = fields.CharField(max_length=48, label='Company Name')
    cmdvdvnm = fields.CharField(max_length=48, label='Name')
    cmdvdvds = fields.CharField(max_length=64, label='Description')
    cmdvadr1 = fields.CharField(max_length=64, label='Address')
    cmdvadr2 = fields.CharField(max_length=64, label='Address')
    cmdvadr3 = fields.CharField(max_length=64, label='Address')
    cmdvzipc = fields.CharField(max_length=32, label='Zip')
    cmdvarid = fields.CharField(max_length=6, label='Area')
    cmdvarnm = fields.CharField(max_length=48, label='Area')
    cmdvstid = fields.CharField(max_length=6, label='State')
    cmdvstnm = fields.CharField(max_length=48, label='State')
    cmdvctid = fields.CharField(max_length=2, label='Country')
    cmdvctnm = fields.CharField(max_length=48, label='Country')
    cmdvphn1 = fields.CharField(max_length=32, label='Phone')
    cmdvphn2 = fields.CharField(max_length=32, label='Phone')
    cmdvfax1 = fields.CharField(max_length=32, label='Fax')
    cmdvfax2 = fields.CharField(max_length=32, label='Fax')
    cmdvxeml = fields.CharField(max_length=64, label='email')
    cmdvwurl = fields.CharField(max_length=64, label='URL')
    cmdvlccd = fields.CharField(max_length=3, label='Local Currency')
    cmdvlccn = fields.CharField(max_length=48, label='Local Currency')
    cmdvlcmt = fields.IntField(label='Currency Conversion Method')
    cmdvlang = fields.CharField(max_length=10, label='Default Language')

    class Meta:
        indexes = [
            UniqueIndex(fields=['cmdvcono', 'cmdvdvno']),
        ]
