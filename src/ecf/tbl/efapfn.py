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


class efapfn(Entity, table=True):
    """API Object Function status"""
    apifncob : str = Field(String(32), label='API Object', primary_key=True)
    apifncnm : str = Field(String(32), label='Function', primary_key=True)
    apifncds : str = Field(String(64), label='Description')
    apifncst : bool = Field(Boolean, label='Status')
    apifnctp : str = Field(String(1), label='Function type')
    apifncsl : bool = Field(Boolean, label='Can Select')
    apifncin : bool = Field(Boolean, label='Can Insert')
    apifncup : bool = Field(Boolean, label='Can Update')
    apifncdl : bool = Field(Boolean, label='Can Delete')
    apifncex : bool = Field(Boolean, label='Can Ext')
    apifaudt : int = Field(Numeric(8, 0), label='Audit date')
    apifautm : int = Field(Numeric(6, 0), label='Audit time')
    apifauus : str = Field(String(24), label='Audit user')
