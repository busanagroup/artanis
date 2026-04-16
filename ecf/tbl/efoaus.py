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


class efoaus(Entity):
    """
    Object Access Group Users
    """

    efougrcd = Field(String(8), label='Obj. Code', primary_key=True, )
    efouusid = Field(String(24), label='User ID', primary_key=True)
    efougrnm = Field(String(24), label='Obj. Name')
    efoufsnm = Field(String(48), label='First Name')
    efoulsnm = Field(String(48), label='Last Name')
    efouaudt = Field(Numeric(8, 0), label='Audit date')
    efouautm = Field(Numeric(6, 0), label='Audit time')
    efouauus = Field(String(24), label='Audit user')
