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

from artanis.sqlentity.entity import *


class efapob(Entity):
    """API Object status"""
    apiobjnm = Field(String(32), label='API Object name', primary_key=True)
    apiobjds = Field(String(64), label='Description')
    apiobjst = Field(Boolean, label='Status')
    apiobjvr = Field(String(16), label='Version')
    apioaudt = Field(Numeric(8, 0), label='Audit date')
    apioautm = Field(Numeric(6, 0), label='Audit time')
    apioauus = Field(String(24), label='Audit user')
