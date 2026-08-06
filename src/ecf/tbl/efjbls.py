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

import typing as t

from artanis.sqlentity import fields
from artanis.sqlentity.sqlorm import Entity

if t.TYPE_CHECKING:
    from ecf.core.jobsvc import JOBSession


class efjbls(Entity):
    """
    Job list management
    """
    jblsidnm = fields.CharField(max_length=38, label='JOB ID', unique=True)
    jblsindt = fields.DecimalField(max_digits=8, decimal_places=0, label='Input Date', index=True)
    jblsintm = fields.DecimalField(max_digits=6, decimal_places=0, label='Input Time', index=True)
    jblsjbtp = fields.IntField(label='Job Type', index=True)
    jblsinid = fields.CharField(max_length=64, label='Input user')
    jblsrqpg = fields.CharField(max_length=24, label='Request PGM')
    jblsrpdt = fields.DecimalField(max_digits=8, decimal_places=0, label='Request date')
    jblsrptm = fields.DecimalField(max_digits=6, decimal_places=0, label='Request time')
    jblsprpg = fields.CharField(max_length=24, label='Job Service Name')
    jblsprdt = fields.DecimalField(max_digits=8, decimal_places=0, label='Job Process Date')
    jblsprtm = fields.DecimalField(max_digits=6, decimal_places=0, label='Job Process Time')
    jblscpdt = fields.DecimalField(max_digits=8, decimal_places=0, label='Job Completion Date')
    jblscptm = fields.DecimalField(max_digits=6, decimal_places=0, label='Job Completion Time')
    jblsprst = fields.IntField(label='Job Status', index=True)
    jblsmdnm = fields.CharField(max_length=24)
    jblsmdid = fields.CharField(max_length=32)
    jblsupdt = fields.DecimalField(max_digits=8, decimal_places=0, label='Last Update Date')
    jblsuptm = fields.DecimalField(max_digits=6, decimal_places=0, label='last Update Time')
    jblssprq = fields.IntField()
    jblsspid = fields.CharField(max_length=24)
    jblsspdt = fields.DecimalField(max_digits=8, decimal_places=0)
    jblssptm = fields.DecimalField(max_digits=6, decimal_places=0)
    jblsprms = fields.CharField(max_length=128, label='Result Message')

    @classmethod
    async def send_job_message(cls, jobsession: 'JOBSession', message: str):
        job_obj = await cls.get(jblsidnm=jobsession.job_id)
        if job_obj:
            job_obj.jblsprms = message[:128] if message else message
            await job_obj.save()
            jobsession.update_job_status(job_obj.jblsprst)

    @classmethod
    async def prepare_rerun(cls, jobid: str, jobtype: int):
        retval = False
        job_obj = await cls.get(jblsidnm=jobid)
        if job_obj and (job_obj.jblsprst == 99):
            job_obj.jblsjbtp = jobtype
            job_obj.jblsprst = 0
            await job_obj.save()
            retval = True
        return retval

    @classmethod
    async def change_job_type(cls, jobid: str, jobtype: int):
        retval = False
        job_obj = await cls.get(jblsidnm=jobid)
        if job_obj and (job_obj.jblsprst == 0):
            retval = True
            job_obj.jblsjbtp = jobtype
            await job_obj.save()
        return retval

    @classmethod
    async def update_job_status(cls, jobid: str, job_status: int):
        retval = False
        jobobj = await cls.get(jblsidnm=jobid)
        if jobobj and (jobobj.jblsprst == 10):
            jobobj.jblsprst = job_status
            await jobobj.save()
            retval = True
        return retval

    @classmethod
    async def get_all_jobs(cls, job_status: int, jobtype: int = 0):
        return await cls.get_all(jblsjbtp=jobtype, jblsprst=job_status)
