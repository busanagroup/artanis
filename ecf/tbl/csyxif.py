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


class csyxif(Entity, table=True):
    """
    Internal System Xtended info
    """
    csyxfoid : str = Field(String(38), label='Info ID', primary_key=True)
    csyxtx08 : str = Field(String(8), label='Value 08')
    csyxtx16 : str = Field(String(16), label='Value 16')
    csyxtx24 : str = Field(String(24), label='Value 24')
    csyxtx32 : str = Field(String(32), label='Value 32')
    csyxtx48 : str = Field(String(48), label='Value 48')
    csyxtx64 : str = Field(String(64), label='Value 64')
    csyxtx128 : str = Field(String(128), label='Value 128')
    csyxival : int = Field(Integer, label='Int Value')
    csyxcval : int = Field(Numeric(15, 2), label='Curr Value')
    csyxdval : int = Field(Numeric(8, 0), label='Date Value')
    csyxtval : int = Field(Numeric(6, 0), label='Time Value')
    csyxdtva : int = Field(Numeric(14, 0), label='Date Time Value')
    csyxblob : bytes = Field(LargeBinary, label='BLOB Data')
    csyxclob : str = Field(TEXT, label='CLOB Data')
    csyxaudt : int = Field(Numeric(8, 0), label='Audit date')
    csyxautm : int = Field(Numeric(6, 0), label='Audit time')
    csyxauus : str = Field(String(24), label='Audit user')
