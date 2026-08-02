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

from artanis.sqlentity import *


class csyjob(Entity, table=True):
    """
    User Defined Job parameters
    """
    cjobcono : str = Field(String(3), label='Company', primary_key=True)
    cjobdvno : str = Field(String(3), label='Division', primary_key=True)
    cjobrqus : str = Field(String(24), label='Requested user', primary_key=True)
    cjobctcd : str = Field(String(10), label='Constant Code', primary_key=True)
    cjobstky : str = Field(String(16), label='Key Value', primary_key=True)
    cjobt161 : str = Field(String(24), label='Value 16')
    cjobt162 : str = Field(String(24), label='Value 16')
    cjobt163 : str = Field(String(24), label='Value 16')
    cjobt164 : str = Field(String(24), label='Value 16')
    cjobt241 : str = Field(String(24), label='Value 24')
    cjobt242 : str = Field(String(24), label='Value 24')
    cjobt243 : str = Field(String(24), label='Value 24')
    cjobt244 : str = Field(String(24), label='Value 24')
    cjobt321 : str = Field(String(24), label='Value 32')
    cjobt322 : str = Field(String(24), label='Value 32')
    cjobt323 : str = Field(String(24), label='Value 32')
    cjobt324 : str = Field(String(24), label='Value 32')
    cjobt481 : str = Field(String(48), label='Value 48')
    cjobt482 : str = Field(String(48), label='Value 48')
    cjobt483 : str = Field(String(48), label='Value 48')
    cjobt484 : str = Field(String(48), label='Value 48')
    cjobt641 : str = Field(String(64), label='Value 64')
    cjobt642 : str = Field(String(64), label='Value 64')
    cjobt643 : str = Field(String(64), label='Value 64')
    cjobt644 : str = Field(String(64), label='Value 64')
    cjobint1 : int = Field(Integer, label='Int Value')
    cjobint2 : int = Field(Integer, label='Int Value')
    cjobint3 : int = Field(Integer, label='Int Value')
    cjobint4 : int = Field(Integer, label='Int Value')
    cjobcur1 : int = Field(Numeric(15, 6), label='Curr Value')
    cjobcur2 : int = Field(Numeric(15, 6), label='Curr Value')
    cjobcur3 : int = Field(Numeric(15, 6), label='Curr Value')
    cjobcur4 : int = Field(Numeric(15, 6), label='Curr Value')
    cjobjbid : str = Field(String(38), label='Job ID', index=True)
    cjobaudt : int = Field(Numeric(8, 0), label='Audit date')
    cjobautm : int = Field(Numeric(6, 0), label='Audit time')
    cjobauus : str = Field(String(24), label='Audit user')
