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

from artanis.sqlentity import *


class csyxif(Entity):
    """
    Internal System Xtended info
    """
    csyxfoid = Field(String(38), label='Info ID', primary_key=True)
    csyxtx08 = Field(String(8), label='Value 08')
    csyxtx16 = Field(String(16), label='Value 16')
    csyxtx24 = Field(String(24), label='Value 24')
    csyxtx32 = Field(String(32), label='Value 32')
    csyxtx48 = Field(String(48), label='Value 48')
    csyxtx64 = Field(String(64), label='Value 64')
    csyxtx128 = Field(String(128), label='Value 128')
    csyxival = Field(Integer, label='Int Value')
    csyxcval = Field(Numeric(15, 2), label='Curr Value')
    csyxdval = Field(Numeric(8, 0), label='Date Value')
    csyxtval = Field(Numeric(6, 0), label='Time Value')
    csyxdtva = Field(Numeric(14, 0), label='Date Time Value')
    csyxblob = Field(LargeBinary, label='BLOB Data')
    csyxclob = Field(TEXT, label='CLOB Data')
    csyxaudt = Field(Numeric(8, 0), label='Audit date')
    csyxautm = Field(Numeric(6, 0), label='Audit time')
    csyxauus = Field(String(24), label='Audit user')

