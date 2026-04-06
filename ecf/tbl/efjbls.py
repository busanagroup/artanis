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

from artanis.sqlentity.sqlorm import *


class efjbls(Entity):
    """
    Job list management
    """
    jblsidnm = Field(String(38), label='JOB ID', primary_key=True)
    jblsindt = Field(Numeric(8, 0), label='Input Date', index=True)
    jblsintm = Field(Numeric(6, 0), label='Input Time', index=True)
    jblsjbtp = Field(Integer, label='Job Type', index=True)
    jblsinid = Field(String(64), label='Input user')
    jblsrqpg = Field(String(24), label='Request PGM')
    jblsrpdt = Field(Numeric(8, 0), label='Request date')
    jblsrptm = Field(Numeric(6, 0), label='Request time')
    jblsprpg = Field(String(24), label='Job Service Name')
    jblsprdt = Field(Numeric(8, 0), label='Job Process Date')
    jblsprtm = Field(Numeric(6, 0), label='Job Process Time')
    jblscpdt = Field(Numeric(8, 0), label='Job Completion Date')
    jblscptm = Field(Numeric(6, 0), label='Job Completion Time')
    jblsprst = Field(Integer, label='Job Status', index=True)
    jblsmdnm = Field(String(24))
    jblsmdid = Field(String(32))
    jblsupdt = Field(Numeric(8, 0), label='Last Update Date')
    jblsuptm = Field(Numeric(6, 0), label='last Update Time')
    jblssprq = Field(Integer)
    jblsspid = Field(String(24))
    jblsspdt = Field(Numeric(8, 0))
    jblssptm = Field(Numeric(6, 0))
    jblsprms = Field(String(128), label='Result Message')
    jblsaudt = Field(Numeric(8, 0), label='Audit date')
    jblsautm = Field(Numeric(6, 0), label='Audit time')
    jblsauus = Field(String(24), label='Audit user')

    @classmethod
    async def send_job_message(cls, jobsession, message, auto_commit=True):
        job_obj = await cls.query.filter_by(jblsidnm=jobsession.job_id).first()
        if job_obj:
            jobsession.update_job_status(job_obj.jblsprst)
            session = Session()
            job_obj.jblsprms = message[:128] if message else message
            if auto_commit and (not session.is_active):
                session.begin()
            try:
                session.add(job_obj)
                if auto_commit:
                    session.commit()
            except:
                if auto_commit:
                    session.rollback()
                    raise

    @classmethod
    async def prepare_rerun(cls, jobid, jobtype, auto_commit=True):
        retval = False
        job_obj = await cls.get([jobid])
        if job_obj and (job_obj.jblsprst == 99):
            job_obj.jblsjbtp = jobtype
            job_obj.jblsprst = 0
            session = Session()
            if auto_commit and (not session.is_active):
                session.begin()
            try:
                session.add(job_obj)
                retval = True
                if auto_commit:
                    session.commit()
            except:
                if auto_commit:
                    session.rollback()
                    raise
        return retval

    @classmethod
    async def change_job_type(cls, jobid, jobtype, auto_commit=True):
        retval = False
        job_obj = await cls.query.filter_by(jblsidnm=jobid).first()
        if job_obj and (job_obj.jblsprst == 0):
            job_obj.jblsjbtp = jobtype
            session = Session()
            if auto_commit and (not session.is_active):
                session.begin()
            try:
                session.add(job_obj)
                retval = True
                if auto_commit:
                    session.commit()
            except:
                if auto_commit:
                    session.rollback()
                    raise
        return retval

    @classmethod
    async def update_job_status(cls, jobid, job_status, auto_commit=True):
        jobobj = await cls.get([jobid])
        session = Session()
        retval = False
        if jobobj and (jobobj.jblsprst == 10):
            if auto_commit and (not session.is_active):
                session.begin()
            try:
                jobobj.jblsprst = job_status
                session.add(jobobj)
                if auto_commit:
                    session.commit()
                retval = True
            except:
                if auto_commit:
                    session.rollback()
                    raise
        return retval

    @classmethod
    async def get_all_jobs(cls, job_status, jobtype: int = 0):
        return await cls.get_all(jblsjbtp=jobtype, jblsprst=job_status)
