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

from artanis.sqlentity import *


class efapfd(Entity, table=True):
    """API Field status"""
    apifldob : str = Field(String(32), label='API Object', primary_key=True)
    apifldfn : str = Field(String(32), label='Function', primary_key=True)
    apifldnm : str = Field(String(32), label='Field', primary_key=True)
    apifldds : str = Field(String(64), label='Description')
    apifldio : int = Field(Integer, label='Input/Output')
    apifldtp : str = Field(String(16), label='Type')
    apifldln : int = Field(Integer, label='Length')
    apifldpr : int = Field(Integer, label='Precision')
    apiflddc : int = Field(Integer, label='Decimal')
    apifldrq : bool = Field(Boolean, label='Required')
    apifaudt : int = Field(Numeric(8, 0), label='Audit date')
    apifautm : int = Field(Numeric(6, 0), label='Audit time')
    apifauus : str = Field(String(24), label='Audit user')
