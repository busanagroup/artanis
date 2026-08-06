#
# Created with IntelliJ IDEA.
# Date: 5/12/20
# Time: 11:36 AM
# To change this template use File | Settings | File Templates.
#

__author__ = 'jaimy'
__version__ = '2.0'
__copyright__ = 'Copyright (c) 2009 My Company'

from artanis.sqlentity import fields
from artanis.sqlentity.sqlorm import Entity


class efjbif(Entity):
    """
    Job List Detail Messages
    """

    jblxidnm = fields.CharField(max_length=38, label='JOB ID', unique=True)
    jblxplif = fields.TextField(label='Extra Information')
    jblxplms = fields.TextField(label='Detail message')
