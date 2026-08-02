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


class cesinf(Entity, table=True):
    """
    User Connect
    """

    csyscono : str = Field(String(3), label='Company', primary_key=True)
    csysdvno : str = Field(String(3), label='Division', primary_key=True)
    csysmocd : str = Field(String(16), label='Module Code', primary_key=True)
    csysctcd : str = Field(String(16), label='Constant Code', primary_key=True)
    csysstky : str = Field(String(48), label='Key Value', primary_key=True)
    csyssbky : str = Field(String(48), label='Sub Key Value', primary_key=True)
    csysstnm : str = Field(String(48), label='Key Name')
    csyssbnm : str = Field(String(48), label='Sub Key Name')
    csystx24 : str = Field(String(24), label='Text 24')
    csystx48 : str = Field(String(48), label='Text 48')
    csyst161 : str = Field(String(16), label='Additional Text 16')
    csyst162 : str = Field(String(16), label='Additional Text 16')
    csyst163 : str = Field(String(16), label='Additional Text 16')
    csyst164 : str = Field(String(16), label='Additional Text 16')
    csyst241 : str = Field(String(24), label='Additional Text 24')
    csyst242 : str = Field(String(24), label='Additional Text 24')
    csyst243 : str = Field(String(24), label='Additional Text 24')
    csyst244 : str = Field(String(24), label='Additional Text 24')
    csyst481 : str = Field(String(48), label='Additional Text 48')
    csyst482 : str = Field(String(48), label='Additional Text 48')
    csyst483 : str = Field(String(48), label='Additional Text 48')
    csyst484 : str = Field(String(48), label='Additional Text 48')
    csysbol1 : int = Field(SmallInteger, label='Additional bool')
    csysbol2 : int = Field(SmallInteger, label='Additional bool')
    csysbol3 : int = Field(SmallInteger, label='Additional bool')
    csysbol4 : int = Field(SmallInteger, label='Additional bool')
    csysint1 : int = Field(Integer, label='Additional Value')
    csysint2 : int = Field(Integer, label='Additional Value')
    csysint3 : int = Field(Integer, label='Additional Value')
    csysint4 : int = Field(Integer, label='Additional Value')
    csyscur1 : int = Field(Numeric(11, 6), label='Additional Value')
    csyscur2 : int = Field(Numeric(11, 6), label='Additional Value')
    csyscur3 : int = Field(Numeric(11, 6), label='Additional Value')
    csyscur4 : int = Field(Numeric(11, 6), label='Additional Value')
    csysaudt : int = Field(Numeric(8, 0), label='Audit date')
    csysautm : int = Field(Numeric(6, 0), label='Audit time')
    csysauus : str = Field(String(24), label='Audit user')
