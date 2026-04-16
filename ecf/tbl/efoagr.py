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


class efoagr(Entity):
    """
    Object Access Group
    """
    efoagrcd = Field(String(8), label='Obj. Code', primary_key=True)
    efoagrnm = Field(String(48), label='Name')
    efoagrds = Field(String(64), label='Description')
    efoaaudt = Field(Numeric(8, 0), label='Audit date')
    efoaautm = Field(Numeric(6, 0), label='Audit time')
    efoaauus = Field(String(24), label='Audit user')
