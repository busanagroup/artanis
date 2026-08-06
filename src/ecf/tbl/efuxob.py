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

__author__ = 'jaimy'
__version__ = '2.0'
__copyright__ = 'Copyright (c) 2014 Busana Apparel Group'

from artanis.sqlentity import fields
from artanis.sqlentity.indexes import UniqueIndex
from artanis.sqlentity.sqlorm import Entity


class efuxob(Entity):
    """
    RPC XML User Access Object
    """
    uxousrnm = fields.CharField(max_length=24, label='User name')
    uxoobjnm = fields.CharField(max_length=24, label='Business Object name')
    uxoofnnm = fields.CharField(max_length=32, label='Function Name')

    class Meta:
        indexes = [
            UniqueIndex(fields=('uxousrnm', 'uxoobjnm', 'uxoofnnm')),
        ]
