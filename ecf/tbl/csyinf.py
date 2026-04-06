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


class csyinf(Entity):
    """
    General System Information Container
    """

    cinfcono = Field(String(3), label='Company', primary_key=True)
    cinfdvno = Field(String(3), label='Division', primary_key=True)
    cinfctcd = Field(String(16), label='Constant Code', primary_key=True)
    cinfstky = Field(String(48), label='Key Value', primary_key=True)
    cinfsbky = Field(String(48), label='Sub Key Value', primary_key=True)
    cinfscky = Field(String(48), label='Linked key Value', index=True)
    cinftx24 = Field(String(24), label='Name')
    cinftx48 = Field(String(48), label='Description')
    cinft241 = Field(String(24), label='Additional Value')
    cinft242 = Field(String(24), label='Additional Value')
    cinft243 = Field(String(24), label='Additional Value')
    cinft244 = Field(String(24), label='Additional Value')
    cinft481 = Field(String(48), label='Additional Value')
    cinft482 = Field(String(48), label='Additional Value')
    cinft483 = Field(String(48), label='Additional Value')
    cinft484 = Field(String(48), label='Additional Value')
    cinft641 = Field(String(64), label='Additional Value')
    cinft642 = Field(String(64), label='Additional Value')
    cinft643 = Field(String(64), label='Additional Value')
    cinft644 = Field(String(64), label='Additional Value')
    cinfint1 = Field(Integer, label='Additional Value')
    cinfint2 = Field(Integer, label='Additional Value')
    cinfint3 = Field(Integer, label='Additional Value')
    cinfint4 = Field(Integer, label='Additional Value')
    cinfcur1 = Field(Numeric(15, 2), label='Additional Value')
    cinfcur2 = Field(Numeric(15, 2), label='Additional Value')
    cinfcur3 = Field(Numeric(15, 2), label='Additional Value')
    cinfcur4 = Field(Numeric(15, 2), label='Additional Value')
    cinfdat1 = Field(Numeric(8, 0), label='Additional Value')
    cinfdat2 = Field(Numeric(8, 0), label='Additional Value')
    cinfdat3 = Field(Numeric(8, 0), label='Additional Value')
    cinfdat4 = Field(Numeric(8, 0), label='Additional Value')
    cinftim1 = Field(Numeric(6, 0), label='Additional Value')
    cinftim2 = Field(Numeric(6, 0), label='Additional Value')
    cinftim3 = Field(Numeric(6, 0), label='Additional Value')
    cinftim4 = Field(Numeric(6, 0), label='Additional Value')
    cinfist1 = Field(Integer, label='Informational Status', index=True)
    cinfist2 = Field(Integer, label='Informational Status', index=True)
    cinfist3 = Field(Integer, label='Informational Status', index=True)
    cinfist4 = Field(Integer, label='Informational Status', index=True)
    cinfaudt = Field(Numeric(8, 0), label='Audit date')
    cinfautm = Field(Numeric(6, 0), label='Audit time')
    cinfauus = Field(String(24), label='Audit user')
