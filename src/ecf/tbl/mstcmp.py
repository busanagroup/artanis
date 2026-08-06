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

from artanis.sqlentity import fields
from artanis.sqlentity.sqlorm import Entity


class mstcmp(Entity):
    """
    Master Company
    """
    cmcpcono = fields.CharField(max_length=3, label='Comp. Code', unique=True)
    cmcpconm = fields.CharField(max_length=48, label='Company Name')
    cmcpcods = fields.CharField(max_length=64, label='Description')
    cmcpadr1 = fields.CharField(max_length=64, label='Address')
    cmcpadr2 = fields.CharField(max_length=64, label='Addr #2')
    cmcpadr3 = fields.CharField(max_length=64, label='Addr #3')
    cmcpzipc = fields.CharField(max_length=48, label='ZIP')
    cmcparid = fields.CharField(max_length=6, label='City')
    cmcparnm = fields.CharField(max_length=48, label='City')
    cmcpstid = fields.CharField(max_length=6, label='State')
    cmcpstnm = fields.CharField(max_length=48, label='State')
    cmcpctid = fields.CharField(max_length=2, label='Country')
    cmcpctnm = fields.CharField(max_length=48, label='Country')
    cmcpphn1 = fields.CharField(max_length=48, label='Phone #1')
    cmcpphn2 = fields.CharField(max_length=48, label='Phone #2')
    cmcpfax1 = fields.CharField(max_length=48, label='Fax #1')
    cmcpfax2 = fields.CharField(max_length=48, label='Fax #2')
    cmcpxeml = fields.CharField(max_length=64, label='E-mail')
    cmcpwurl = fields.CharField(max_length=64, label='Website')
    cmcpmcst = fields.IntField(label='Multi Currency')
    cmcpcucd = fields.CharField(max_length=3, label='Currency')
    cmcpcunm = fields.CharField(max_length=48, label='Currency')
    cmcprtcd = fields.CharField(max_length=3, label='Rate')
    cmcprtnm = fields.CharField(max_length=48, label='Rate')
