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

from artanis.sqlentity.sqlorm import *


class efuxob(Entity):
    """
    RPC XML User Access Object
    """
    uxousrnm = Field(String(24), label='User name', primary_key=True)
    uxoobjnm = Field(String(24), label='Business Object name', primary_key=True)
    uxoofnnm = Field(String(32), label='Function Name', primary_key=True)
    uxooaudt = Field(Numeric(8, 0), label='Audit date')
    uxooautm = Field(Numeric(6, 0), label='Audit time')
    uxooauus = Field(String(24), label='Audit user')
