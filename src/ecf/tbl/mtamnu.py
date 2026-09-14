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


class mtamnu(Entity):
    """
    Meta Menu
    """
    mtmnvrid = fields.IntField(label='Menu Version ID')
    mtmncrck = fields.CharField(max_length=1024, label='Condition to check')
    mtmnvsst = fields.BooleanField(label='Visible')
    mtmnicon = fields.CharField(max_length=255, label='Icon')
    mtmnicbg = fields.CharField(max_length=255, label='Icon Background')
    mtmnlfmn = fields.BooleanField(label='Left Menu')
    mtmnlink = fields.CharField(max_length=255, label='Link')
    mtmnmomn = fields.BooleanField(label='Mobile Menu')
    mtmnmocd = fields.CharField(max_length=48, label='Module Code')
    mtmnmock = fields.CharField(max_length=255, label='Module to check')
    mtmnmonm = fields.CharField(max_length=64, label='Module Name')
    mtmnorsq = fields.IntField(label='Order Sequence')
    mtmnprio = fields.IntField(label='Priority')
    mtmntags = fields.CharField(max_length=255, label='Tags')
    mtmntgct = fields.BooleanField(label='Tag Count')
    mtmntggt = fields.CharField(max_length=255, label='Tag Get')
    mtmntgsy = fields.CharField(max_length=255, label='Tag Style')
    mtmntitl = fields.CharField(max_length=64, label='Title')
    mtmnxmid = fields.CharField(max_length=48, label='XML Identifier')
    mtmnacid = fields.UUIDField(label='Action ID')
    mtmnprid = fields.UUIDField(label='Parent ID')
    mtmnusid = fields.UUIDField(label='User ID')
