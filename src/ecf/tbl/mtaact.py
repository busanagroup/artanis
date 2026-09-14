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
__copyright__ = 'Copyright (c) 2026 Busana Apparel Group'

from artanis.sqlentity import fields
from artanis.sqlentity.indexes import Index
from artanis.sqlentity.sqlorm import Entity


class mtaact(Entity):
    """
    Meta Action
    """
    mtachome = fields.BooleanField(label='Home')
    mtacctid = fields.CharField(max_length=24, label='Controller Name')
    mtacmoid = fields.CharField(max_length=48, label='Module')
    mtacacnm = fields.CharField(max_length=48, label='Action Name')
    mtacactp = fields.CharField(max_length=48, label='Action Type')
    mtacprio = fields.IntField(label='Priority')
    mtacxmid = fields.CharField(max_length=48, label='XML Identifier')
    mtacoxml = fields.TextField(label='XML Content')
    mtacojsn = fields.TextField(label='JSON Content')

    class Meta:
        indexes = [
            Index(fields=('mtacacnm', 'mtacactp')),
        ]
