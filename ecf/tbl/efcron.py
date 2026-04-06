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

from artanis.sqlentity.entity import *


class efcron(Entity):
    """
    Cron JOB Services
    """
    crjbidcd = Field(String(3), label="Cron ID", primary_key=True)
    crjbjbst = Field(Integer, label="Active Status", index=True)
    crjbsch1 = Field(String(64), label="Minute")
    crjbsch2 = Field(String(64), label="Hour")
    crjbsch3 = Field(String(64), label="Day")
    crjbsch4 = Field(String(64), label="Month")
    crjbsch5 = Field(String(64), label="DOW")
    crjbjprg = Field(String(6), label="Program")
    crjbjtbl = Field(String(6), label="Table")
    crjbjbcd = Field(String(12), label="JOB Service")
    crjbjfld = Field(String(8), label="Field Name")
    crjbjfva = Field(String(8), label="Unique Value")
    crjbjbld = Field(String(8), label='Job Identifier Field')
    crjbrsus = Field(String(24), label='Responsible user')
    crjbexdt = Field(Numeric(8, 0), label='Last executed date')
    crjbextm = Field(Numeric(6, 0), label='Last executed time')
    crjbaudt = Field(Numeric(8, 0), label='Audit date')
    crjbautm = Field(Numeric(6, 0), label='Audit time')
    crjbauus = Field(String(24), label='Audit user')

    @classmethod
    async def get_all_tasks(cls, task_status):
        return await cls.get_all(crjbjbst=task_status)
