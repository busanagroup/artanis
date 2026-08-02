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


class cmpdiv(Entity, table=True):
    """
    Company division
    """

    cmdvcono : str = Field(String(3), primary_key=True, nullable=True, label='Company')
    cmdvdvno : str = Field(String(3), primary_key=True, nullable=True, label='Division')
    cmdvconm : str = Field(String(48), label='Company Name')
    cmdvdvnm : str = Field(String(48), label='Name')
    cmdvdvds : str = Field(String(64), label='Description')
    cmdvadr1 : str = Field(String(64), label='Address')
    cmdvadr2 : str = Field(String(64), label='Address')
    cmdvadr3 : str = Field(String(64), label='Address')
    cmdvzipc : str = Field(String(32), label='Zip')
    cmdvarid : str = Field(String(6), label='Area')
    cmdvarnm : str = Field(String(48), label='Area')
    cmdvstid : str = Field(String(6), label='State')
    cmdvstnm : str = Field(String(48), label='State')
    cmdvctid : str = Field(String(2), label='Country')
    cmdvctnm : str = Field(String(48), label='Country')
    cmdvphn1 : str = Field(String(32), label='Phone')
    cmdvphn2 : str = Field(String(32), label='Phone')
    cmdvfax1 : str = Field(String(32), label='Fax')
    cmdvfax2 : str = Field(String(32), label='Fax')
    cmdvxeml : str = Field(String(64), label='email')
    cmdvwurl : str = Field(String(64), label='URL')
    cmdvlccd : str = Field(String(3), label='Local Currency')
    cmdvlccn : str = Field(String(48), label='Local Currency')
    cmdvlcmt : int = Field(Integer, label='Currency Conversion Method')
    cmdvlang : str = Field(String(10), label='Default Language')
    cmdvaudt : int = Field(Numeric(8, 0), label='Audit date')
    cmdvautm : int = Field(Numeric(6, 0), label='Audit time')
    cmdvauus : str = Field(String(24), label='Audit user')
