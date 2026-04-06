#
# Created with IntelliJ IDEA.
# Date: 5/12/20
# Time: 11:36 AM
# To change this template use File | Settings | File Templates.
#

__author__ = 'jaimy'
__version__ = '2.0'
__copyright__ = 'Copyright (c) 2009 My Company'

from artanis.sqlentity.sqlorm import *


class efjbif(Entity):
    """
    Job List Detail Messages
    """

    jblxidnm = Field(String(38), label='JOB ID', primary_key=True)
    jblxplif = Field(TEXT, label='Extra Information')
    jblxplms = Field(TEXT, label='Detail message')
    jblxaudt = Field(Numeric(8, 0), label='Audit date')
    jblxautm = Field(Numeric(6, 0), label='Audit time')
    jblxauus = Field(String(24), label='Audit user')
