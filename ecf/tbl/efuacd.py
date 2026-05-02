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


class efuacd(Entity, table=True):
    """
    Alternate User Division
    """
    efususid : str = Field(String(24), label='User ID', primary_key=True)
    efuscono : str = Field(String(3), label='Comp. ID', primary_key=True)
    efusdvno : str = Field(String(3), label='Division', primary_key=True)
    efusfsnm : str = Field(String(48), label='First Name')
    efuslsnm : str = Field(String(48), label='Last Name')
    efusconm : str = Field(String(48), label='Comp. ID')
    efusdvnm : str = Field(String(48), label='Division')
    efusaudt : int = Field(Numeric(8, 0), label='Audit date')
    efusautm : int = Field(Numeric(6, 0), label='Audit time')
    efusauus : str = Field(String(24), label='Audit user')
