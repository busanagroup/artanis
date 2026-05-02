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


class mstcmp(Entity, table=True):
    """
    Master Company
    """
    cmcpcono : str = Field(String(3), label='Comp. Code', primary_key=True, nullable=True)
    cmcpconm : str = Field(String(48), label='Company Name')
    cmcpcods : str = Field(String(64), label='Description')
    cmcpadr1 : str = Field(String(64), label='Address')
    cmcpadr2 : str = Field(String(64), label='Addr #2')
    cmcpadr3 : str = Field(String(64), label='Addr #3')
    cmcpzipc : str = Field(String(48), label='ZIP')
    cmcparid : str = Field(String(6), label='City')
    cmcparnm : str = Field(String(48), label='City')
    cmcpstid : str = Field(String(6), label='State')
    cmcpstnm : str = Field(String(48), label='State')
    cmcpctid : str = Field(String(2), label='Country')
    cmcpctnm : str = Field(String(48), label='Country')
    cmcpphn1 : str = Field(String(48), label='Phone #1')
    cmcpphn2 : str = Field(String(48), label='Phone #2')
    cmcpfax1 : str = Field(String(48), label='Fax #1')
    cmcpfax2 : str = Field(String(48), label='Fax #2')
    cmcpxeml : str = Field(String(64), label='E-mail')
    cmcpwurl : str = Field(String(64), label='Website')
    cmcpmcst : int = Field(Integer, label='Multi Currency')
    cmcpcucd : str = Field(String(3), label='Currency')
    cmcpcunm : str = Field(String(48), label='Currency')
    cmcprtcd : str = Field(String(3), label='Rate')
    cmcprtnm : str = Field(String(48), label='Rate')
    cmcpaudt : int = Field(Numeric(8, 0), label='Audit date')
    cmcpautm : int = Field(Numeric(6, 0), label='Audit time')
    cmcpauus : str = Field(String(24), label='Audit user')
