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


class mstcmp(Entity):
    """
    Master Company
    """
    cmcpcono = Field(String(3), primary_key=True, nullable=True)
    cmcpconm = Field(String(24))
    cmcpcods = Field(String(48))
    cmcpadr1 = Field(String(48))
    cmcpadr2 = Field(String(48))
    cmcpadr3 = Field(String(48))
    cmcpzipc = Field(String(48))
    cmcparid = Field(String(6))
    cmcparnm = Field(String(16))
    cmcpstid = Field(String(6))
    cmcpstnm = Field(String(16))
    cmcpctid = Field(String(2))
    cmcpctnm = Field(String(16))
    cmcpphn1 = Field(String(24))
    cmcpphn2 = Field(String(24))
    cmcpfax1 = Field(String(24))
    cmcpfax2 = Field(String(24))
    cmcpxeml = Field(String(32))
    cmcpwurl = Field(String(48))
    cmcpmcst = Field(Integer)
    cmcpcucd = Field(String(3))
    cmcpcunm = Field(String(16))
    cmcprtcd = Field(String(3))
    cmcprtnm = Field(String(16))
    cmcpaudt = Field(Numeric(8, 0))
    cmcpautm = Field(Numeric(6, 0))
    cmcpauus = Field(String(24))
