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

from artanis.sqlentity.sqlorm import *


class cesinf(Entity):
    """
    User Connect
    """

    csyscono = Field(String(3), label='Company', primary_key=True)
    csysdvno = Field(String(3), label='Division', primary_key=True)
    csysmocd = Field(String(16), label='Module Code', primary_key=True)
    csysctcd = Field(String(16), label='Constant Code', primary_key=True)
    csysstky = Field(String(48), label='Key Value', primary_key=True)
    csyssbky = Field(String(48), label='Sub Key Value', primary_key=True)
    csysstnm = Field(String(24), label='Key Name')
    csyssbnm = Field(String(24), label='Sub Key Name')
    csystx24 = Field(String(24), label='Text 24')
    csystx48 = Field(String(48), label='Text 48')
    csyst161 = Field(String(16), label='Additional Text 16')
    csyst162 = Field(String(16), label='Additional Text 16')
    csyst163 = Field(String(16), label='Additional Text 16')
    csyst164 = Field(String(16), label='Additional Text 16')
    csyst241 = Field(String(24), label='Additional Text 24')
    csyst242 = Field(String(24), label='Additional Text 24')
    csyst243 = Field(String(24), label='Additional Text 24')
    csyst244 = Field(String(24), label='Additional Text 24')
    csyst481 = Field(String(48), label='Additional Text 48')
    csyst482 = Field(String(48), label='Additional Text 48')
    csyst483 = Field(String(48), label='Additional Text 48')
    csyst484 = Field(String(48), label='Additional Text 48')
    csysbol1 = Field(SmallInteger, label='Additional bool')
    csysbol2 = Field(SmallInteger, label='Additional bool')
    csysbol3 = Field(SmallInteger, label='Additional bool')
    csysbol4 = Field(SmallInteger, label='Additional bool')
    csysint1 = Field(Integer, label='Additional Value')
    csysint2 = Field(Integer, label='Additional Value')
    csysint3 = Field(Integer, label='Additional Value')
    csysint4 = Field(Integer, label='Additional Value')
    csyscur1 = Field(Numeric(11, 6), label='Additional Value')
    csyscur2 = Field(Numeric(11, 6), label='Additional Value')
    csyscur3 = Field(Numeric(11, 6), label='Additional Value')
    csyscur4 = Field(Numeric(11, 6), label='Additional Value')
    csysaudt = Field(Numeric(8, 0), label='Audit date')
    csysautm = Field(Numeric(6, 0), label='Audit time')
    csysauus = Field(String(24), label='Audit user')
