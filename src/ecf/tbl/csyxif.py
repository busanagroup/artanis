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

__author__ = 'jaimy'
__version__ = '2.0'
__copyright__ = 'Copyright (c) 2014 Busana Apparel Group'

from artanis.sqlentity import fields
from artanis.sqlentity.sqlorm import Entity


class csyxif(Entity):
    """
    Internal System Xtended info
    """
    csyxfoid = fields.CharField(max_length=38, label='Info ID', unique=True)
    csyxtx08 = fields.CharField(max_length=8, label='Value 08')
    csyxtx16 = fields.CharField(max_length=16, label='Value 16')
    csyxtx24 = fields.CharField(max_length=24, label='Value 24')
    csyxtx32 = fields.CharField(max_length=32, label='Value 32')
    csyxtx48 = fields.CharField(max_length=48, label='Value 48')
    csyxtx64 = fields.CharField(max_length=64, label='Value 64')
    csyxtx128 = fields.CharField(max_length=128, label='Value 128')
    csyxival = fields.IntField(label='Int Value')
    csyxcval = fields.DecimalField(max_digits=15, decimal_places=2, label='Curr Value')
    csyxdval = fields.DecimalField(max_digits=8, decimal_places=0, label='Date Value')
    csyxtval = fields.DecimalField(max_digits=6, decimal_places=0, label='Time Value')
    csyxdtva = fields.DecimalField(max_digits=14, decimal_places=0, label='Date Time Value')
    csyxblob = fields.BinaryField(label='BLOB Data')
    csyxclob = fields.TextField(label='CLOB Data')
