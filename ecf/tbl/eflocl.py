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

from artanis.sqlentity.sqlorm import *


class eflocl(Entity):
    """
    Locale message
    """
    eflclccd = Field(String(16), primary_key=True, label='Language ID')
    eflcmdcd = Field(String(32), primary_key=True, label='Module')
    eflcmsid = Field(String(32), primary_key=True, label='Hash ID')
    eflcmdtp = Field(Integer, label='Module type')
    eflcmssr = Field(String(250), label='Message')
    eflcmsls = Field(String(250), label='Translation')
    eflcaudt = Field(Numeric(8, 0), label='Audit user')
    eflcautm = Field(Numeric(6, 0), label='Audit time')
    eflcauus = Field(String(24), label='Audit user')
