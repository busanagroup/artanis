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


class efapfd(Entity):
    """API Field status"""
    apifldob = Field(String(32), label='API Object', primary_key=True)
    apifldfn = Field(String(32), label='Function', primary_key=True)
    apifldnm = Field(String(32), label='Field', primary_key=True)
    apifldds = Field(String(64), label='Description')
    apifldio = Field(Integer, label='Input/Output')
    apifldtp = Field(String(16), label='Type')
    apifldln = Field(Integer, label='Length')
    apifldpr = Field(Integer, label='Precision')
    apiflddc = Field(Integer, label='Decimal')
    apifldrq = Field(Boolean, label='Required')
    apifaudt = Field(Numeric(8, 0), label='Audit date')
    apifautm = Field(Numeric(6, 0), label='Audit time')
    apifauus = Field(String(24), label='Audit user')
