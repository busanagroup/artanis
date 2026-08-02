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


class csyinf(Entity, table=True):
    """
    General System Information Container
    """

    cinfcono : str = Field(String(3), label='Company', primary_key=True)
    cinfdvno : str = Field(String(3), label='Division', primary_key=True)
    cinfctcd : str = Field(String(16), label='Constant Code', primary_key=True)
    cinfstky : str = Field(String(48), label='Key Value', primary_key=True)
    cinfsbky : str = Field(String(48), label='Sub Key Value', primary_key=True)
    cinfscky : str = Field(String(48), label='Linked key Value', index=True)
    cinftx24 : str = Field(String(24), label='Name')
    cinftx48 : str = Field(String(48), label='Description')
    cinft241 : str = Field(String(24), label='Additional Value')
    cinft242 : str = Field(String(24), label='Additional Value')
    cinft243 : str = Field(String(24), label='Additional Value')
    cinft244 : str = Field(String(24), label='Additional Value')
    cinft481 : str = Field(String(48), label='Additional Value')
    cinft482 : str = Field(String(48), label='Additional Value')
    cinft483 : str = Field(String(48), label='Additional Value')
    cinft484 : str = Field(String(48), label='Additional Value')
    cinft641 : str = Field(String(64), label='Additional Value')
    cinft642 : str = Field(String(64), label='Additional Value')
    cinft643 : str = Field(String(64), label='Additional Value')
    cinft644 : str = Field(String(64), label='Additional Value')
    cinfint1 : int = Field(Integer, label='Additional Value')
    cinfint2 : int = Field(Integer, label='Additional Value')
    cinfint3 : int = Field(Integer, label='Additional Value')
    cinfint4 : int = Field(Integer, label='Additional Value')
    cinfcur1 : int = Field(Numeric(15, 2), label='Additional Value')
    cinfcur2 : int = Field(Numeric(15, 2), label='Additional Value')
    cinfcur3 : int = Field(Numeric(15, 2), label='Additional Value')
    cinfcur4 : int = Field(Numeric(15, 2), label='Additional Value')
    cinfdat1 : int = Field(Numeric(8, 0), label='Additional Value')
    cinfdat2 : int = Field(Numeric(8, 0), label='Additional Value')
    cinfdat3 : int = Field(Numeric(8, 0), label='Additional Value')
    cinfdat4 : int = Field(Numeric(8, 0), label='Additional Value')
    cinftim1 : int = Field(Numeric(6, 0), label='Additional Value')
    cinftim2 : int = Field(Numeric(6, 0), label='Additional Value')
    cinftim3 : int = Field(Numeric(6, 0), label='Additional Value')
    cinftim4 : int = Field(Numeric(6, 0), label='Additional Value')
    cinfist1 : int = Field(Integer, label='Informational Status', index=True)
    cinfist2 : int = Field(Integer, label='Informational Status', index=True)
    cinfist3 : int = Field(Integer, label='Informational Status', index=True)
    cinfist4 : int = Field(Integer, label='Informational Status', index=True)
    cinfaudt : int = Field(Numeric(8, 0), label='Audit date')
    cinfautm : int = Field(Numeric(6, 0), label='Audit time')
    cinfauus : str = Field(String(24), label='Audit user')
