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


class efcron(Entity):
    """
    Cron JOB Services
    """
    crjbidcd = fields.CharField(max_length=3, label="Cron ID", unique=True)
    crjbjbst = fields.IntField(label="Active Status", index=True)
    crjbsch1 = fields.CharField(max_length=64, label="Minute")
    crjbsch2 = fields.CharField(max_length=64, label="Hour")
    crjbsch3 = fields.CharField(max_length=64, label="Day")
    crjbsch4 = fields.CharField(max_length=64, label="Month")
    crjbsch5 = fields.CharField(max_length=64, label="DOW")
    crjbjprg = fields.CharField(max_length=6, label="Program")
    crjbjtbl = fields.CharField(max_length=6, label="Table")
    crjbjbcd = fields.CharField(max_length=12, label="JOB Service")
    crjbjfld = fields.CharField(max_length=8, label="Field Name")
    crjbjfva = fields.CharField(max_length=8, label="Unique Value")
    crjbjbld = fields.CharField(max_length=8, label='Job Identifier Field')
    crjbrsus = fields.CharField(max_length=24, label='Responsible user')
    crjbexdt = fields.DecimalField(max_digits=8, decimal_places=0, label='Last executed date')
    crjbextm = fields.DecimalField(max_digits=6, decimal_places=0, label='Last executed time')

    @classmethod
    async def get_all_tasks(cls, task_status):
        return await cls.get_all(crjbjbst=task_status)
