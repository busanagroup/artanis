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

from artanis.sqlentity.entity import *


class csyjob(Entity):
    """
    User Defined Job parameters
    """
    cjobcono = Field(String(3), label='Company', primary_key=True)
    cjobdvno = Field(String(3), label='Division', primary_key=True)
    cjobrqus = Field(String(24), label='Requested user', primary_key=True)
    cjobctcd = Field(String(10), label='Constant Code', primary_key=True)
    cjobstky = Field(String(16), label='Key Value', primary_key=True)
    cjobt161 = Field(String(24), label='Value 16')
    cjobt162 = Field(String(24), label='Value 16')
    cjobt163 = Field(String(24), label='Value 16')
    cjobt164 = Field(String(24), label='Value 16')
    cjobt241 = Field(String(24), label='Value 24')
    cjobt242 = Field(String(24), label='Value 24')
    cjobt243 = Field(String(24), label='Value 24')
    cjobt244 = Field(String(24), label='Value 24')
    cjobt321 = Field(String(24), label='Value 32')
    cjobt322 = Field(String(24), label='Value 32')
    cjobt323 = Field(String(24), label='Value 32')
    cjobt324 = Field(String(24), label='Value 32')
    cjobt481 = Field(String(48), label='Value 48')
    cjobt482 = Field(String(48), label='Value 48')
    cjobt483 = Field(String(48), label='Value 48')
    cjobt484 = Field(String(48), label='Value 48')
    cjobt641 = Field(String(64), label='Value 64')
    cjobt642 = Field(String(64), label='Value 64')
    cjobt643 = Field(String(64), label='Value 64')
    cjobt644 = Field(String(64), label='Value 64')
    cjobint1 = Field(Integer, label='Int Value')
    cjobint2 = Field(Integer, label='Int Value')
    cjobint3 = Field(Integer, label='Int Value')
    cjobint4 = Field(Integer, label='Int Value')
    cjobcur1 = Field(Numeric(15, 6), label='Curr Value')
    cjobcur2 = Field(Numeric(15, 6), label='Curr Value')
    cjobcur3 = Field(Numeric(15, 6), label='Curr Value')
    cjobcur4 = Field(Numeric(15, 6), label='Curr Value')
    cjobjbid = Field(String(38), label='Job ID', index=True)
    cjobaudt = Field(Numeric(8, 0), label='Audit date')
    cjobautm = Field(Numeric(6, 0), label='Audit time')
    cjobauus = Field(String(24), label='Audit user')
