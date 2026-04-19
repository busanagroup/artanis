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
    cmcpcono = Field(String(3), label='Comp. Code', primary_key=True, nullable=True)
    cmcpconm = Field(String(48), label='Company Name')
    cmcpcods = Field(String(64), label='Description')
    cmcpadr1 = Field(String(64), label='Address')
    cmcpadr2 = Field(String(64), label='Addr #2')
    cmcpadr3 = Field(String(64), label='Addr #3')
    cmcpzipc = Field(String(48), label='ZIP')
    cmcparid = Field(String(6), label='City')
    cmcparnm = Field(String(48), label='City')
    cmcpstid = Field(String(6), label='State')
    cmcpstnm = Field(String(48), label='State')
    cmcpctid = Field(String(2), label='Country')
    cmcpctnm = Field(String(48), label='Country')
    cmcpphn1 = Field(String(48), label='Phone #1')
    cmcpphn2 = Field(String(48), label='Phone #2')
    cmcpfax1 = Field(String(48), label='Fax #1')
    cmcpfax2 = Field(String(48), label='Fax #2')
    cmcpxeml = Field(String(64), label='E-mail')
    cmcpwurl = Field(String(64), label='Website')
    cmcpmcst = Field(Integer, label='Multi Currency')
    cmcpcucd = Field(String(3), label='Currency')
    cmcpcunm = Field(String(48), label='Currency')
    cmcprtcd = Field(String(3), label='Rate')
    cmcprtnm = Field(String(48), label='Rate')
    cmcpaudt = Field(Numeric(8, 0), label='Audit date')
    cmcpautm = Field(Numeric(6, 0), label='Audit time')
    cmcpauus = Field(String(24), label='Audit user')
