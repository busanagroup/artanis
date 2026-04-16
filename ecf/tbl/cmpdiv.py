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


class cmpdiv(Entity):
    """
    Company division
    """

    cmdvcono = Field(String(3), primary_key=True, nullable=True, label='Company')
    cmdvdvno = Field(String(3), primary_key=True, nullable=True, label='Division')
    cmdvconm = Field(String(48), label='Company Name')
    cmdvdvnm = Field(String(48), label='Name')
    cmdvdvds = Field(String(64), label='Description')
    cmdvadr1 = Field(String(64), label='Address')
    cmdvadr2 = Field(String(64), label='Address')
    cmdvadr3 = Field(String(64), label='Address')
    cmdvzipc = Field(String(32), label='Zip')
    cmdvarid = Field(String(6), label='Area')
    cmdvarnm = Field(String(48), label='Area')
    cmdvstid = Field(String(6), label='State')
    cmdvstnm = Field(String(48), label='State')
    cmdvctid = Field(String(2), label='Country')
    cmdvctnm = Field(String(48), label='Country')
    cmdvphn1 = Field(String(32), label='Phone')
    cmdvphn2 = Field(String(32), label='Phone')
    cmdvfax1 = Field(String(32), label='Fax')
    cmdvfax2 = Field(String(32), label='Fax')
    cmdvxeml = Field(String(64), label='email')
    cmdvwurl = Field(String(64), label='URL')
    cmdvlccd = Field(String(3), label='Local Currency')
    cmdvlccn = Field(String(48), label='Local Currency')
    cmdvlcmt = Field(Integer, label='Currency Conversion Method')
    cmdvlang = Field(String(10), label='Default Language')
    cmdvaudt = Field(Numeric(8, 0), label='Audit date')
    cmdvautm = Field(Numeric(6, 0), label='Audit time')
    cmdvauus = Field(String(24), label='Audit user')
