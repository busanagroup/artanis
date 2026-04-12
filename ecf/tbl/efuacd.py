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


class efuacd(Entity):
    """
    Alternate User Division
    """
    efususid = Field(String(24), label='User ID', primary_key=True)
    efuscono = Field(String(3), label='Comp. ID', primary_key=True)
    efusdvno = Field(String(3), label='Division', primary_key=True)
    efusfsnm = Field(String(24), label='First Name')
    efuslsnm = Field(String(24), label='Last Name')
    efusconm = Field(String(24), label='Comp. ID')
    efusdvnm = Field(String(24), label='Division')
    efusaudt = Field(Numeric(8, 0), label='Audit date')
    efusautm = Field(Numeric(6, 0), label='Audit time')
    efusauus = Field(String(24), label='Audit user')
