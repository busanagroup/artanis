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

from artanis.sqlentity import *


class efcron(Entity, table=True):
    """
    Cron JOB Services
    """
    crjbidcd : str = Field(String(3), label="Cron ID", primary_key=True)
    crjbjbst : int = Field(Integer, label="Active Status", index=True)
    crjbsch1 : str = Field(String(64), label="Minute")
    crjbsch2 : str = Field(String(64), label="Hour")
    crjbsch3 : str = Field(String(64), label="Day")
    crjbsch4 : str = Field(String(64), label="Month")
    crjbsch5 : str = Field(String(64), label="DOW")
    crjbjprg : str = Field(String(6), label="Program")
    crjbjtbl : str = Field(String(6), label="Table")
    crjbjbcd : str = Field(String(12), label="JOB Service")
    crjbjfld : str = Field(String(8), label="Field Name")
    crjbjfva : str = Field(String(8), label="Unique Value")
    crjbjbld : str = Field(String(8), label='Job Identifier Field')
    crjbrsus : str = Field(String(24), label='Responsible user')
    crjbexdt : int = Field(Numeric(8, 0), label='Last executed date')
    crjbextm : int = Field(Numeric(6, 0), label='Last executed time')
    crjbaudt : int = Field(Numeric(8, 0), label='Audit date')
    crjbautm : int = Field(Numeric(6, 0), label='Audit time')
    crjbauus : str = Field(String(24), label='Audit user')

    @classmethod
    async def get_all_tasks(cls, task_status):
        return await cls.get_all(crjbjbst=task_status)
