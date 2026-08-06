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

from artanis.sqlentity import fields
from artanis.sqlentity.sqlorm import Entity


class efoagr(Entity):
    """
    Object Access Group
    """
    efoagrcd = fields.CharField(max_length=8, label='Obj. Code', unique=True)
    efoagrnm = fields.CharField(max_length=48, label='Name')
    efoagrds = fields.CharField(max_length=64, label='Description')
