#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Busana Apparel Group. All rights reserved.
#
# This product and it's source code is protected by patents, copyright laws and
# international copyright treaties, as well as other intellectual property
# laws and treaties. The product is licensed, not sold.
#
# The source code and sample programs in this package or parts hereof
# as well as the documentation shall not be copied, modified or redistributed
# without permission, explicit or implied, of the author.
#
# This module is part of Artanis Enterprise Platform and is released under
# the Apache-2.0 License: https://www.apache.org/licenses/LICENSE-2.0
import datetime as dt
import enum
from typing import Any

from taskiq.kicker import AsyncKicker

from artanis.component.validators import validators
from artanis.sqlentity import entity
from artanis.sqlentity.baseid import MSSortableUID
from artanis.sqlentity.sqlorm import Session
from artanis.taskiq.broker import broker, task_broker
from artanis.taskiq.proxy import JobObjectProxy
from artanis.taskiq.tasks import TaskType, JOBType
from ecf.core.ecfcmn import BaseController


@enum.unique
class JOBStatus(enum.Enum):
    JST_UNASSIGNED = 10
    JST_BUSY = 20
    JST_COMPLETED = 30
    JST_ERROR = 99


class JOBSession:

    def __init__(self, job_id: str | None = None):
        self.job_id = job_id
        self.processing_job = None
        self.processing_status: JOBStatus = JOBStatus.JST_UNASSIGNED
        self.job_status = 0

    def update_job_status(self, status):
        self.job_status = status

    def is_canceling(self):
        return self.job_status == 15


class JobAssignment(object):

    def __init__(self,
                 sender: BaseController,
                 job_service_name: str,
                 immediate: bool = False):
        self.sender = sender
        self.timestamp = dt.datetime.now()
        self.job_id = MSSortableUID(self.timestamp)
        self.service_name = sender.get_service_name()
        self.job_service_name = job_service_name
        self.immediate = immediate
        self.description: str | None = None
        self.user_name: str | None = None

    async def execute_job(self):
        await JobRunner(self.sender.get_request(), self.job_service_name, str(self.job_id))

    async def assign_job(self, immediate=False, auto_commit=True, attachment: dict = None):
        validators.NotEmpty(messages={'empty': "service name has not been assigned"}).to_python(self.service_name)
        validators.NotEmpty(messages={'empty': "job service name has not been assigned"}).to_python(
            self.job_service_name)
        csyxif = entity.get_entity('csyxif')
        efjbls = entity.get_entity('efjbls')
        efjbif = entity.get_entity('efjbif')

        session = Session()
        try:
            obj = efjbls.query.filter_by(jblsidnm=self.job_id).first()
            lob = efjbif.query.filter_by(jblxidnm=self.job_id).first()
            validators.Assertion(messages={'assert': 'existing jobID has been existed'}).to_python(not (obj or lob))
            now = dt.datetime.now()
            rec = efjbls(
                jblsidnm=str(self.job_id),
                jblsindt=self.timestamp.date().tointeger(),
                jblsintm=self.timestamp.time().tointeger(),
                jblsjbtp=0,
                jblsinid=self.description,
                jblsrqpg=self.service_name,
                jblsrpdt=0,
                jblsrptm=0,
                jblsprpg=self.job_service_name,
                jblsprst=0,
                jblsaudt=now.date().tointeger(),
                jblsautm=now.time().tointeger(),
                jblsauus=self.user_name)
            lrec = efjbif(
                jblxidnm=self.job_id,
                jblxaudt=now.date().tointeger(),
                jblxautm=now.time().tointeger(),
                jblxauus=self.user_name)

            if auto_commit:
                if not session.is_active:
                    session.begin()
            try:
                if attachment and isinstance(attachment, dict):
                    attachment['csyxfoid'] = str(self.job_id)
                    attachment_obj = csyxif(**attachment)
                    session.add(attachment_obj)
                session.add(rec)
                session.add(lrec)
                if auto_commit:
                    await session.commit()
            except:
                if auto_commit:
                    await session.rollback()
                raise
        finally:
            if immediate:
                await self.execute_job()


class BaseJobEngine(BaseController):
    __JOB_TYPE__: int = JOBType.REGULAR_JOB

    async def __getsession__(self, *args, **kwargs):
        session = JOBSession()
        return session

    async def execute(self, session):
        raise NotImplementedError


class JobEngine(BaseJobEngine): ...


class JobRunner:

    def __init__(self, request: Any, job_service: str, job_id: str):
        self.job_id = job_id
        self.request = request
        self.job_service = job_service

    def __await__(self):
        return self.dispatch().__await__()

    async def get_username(self):
        if not self.request:
            return None
        if hasattr(self.request, 'user'):
            user_name = self.request.user.username
        else:
            user_name = self.request.user_name
        return user_name

    async def dispatch(self):
        job_channel = broker if self.get_task_type() == JOBType.REGULAR_JOB else task_broker
        efjbls = BaseController.get_entity('efjbls')
        await efjbls.change_job_type(self.job_id, 1)
        await AsyncKicker(
            broker=job_channel,
            task_name="artanis_task",
            labels={}
        ).kiq(
            TaskType.TK_JOB,
            self.get_username(),
            self.job_id
        )

    def get_task_type(self):
        proxy = JobObjectProxy(self.request)
        service_class = proxy.get_service_class(self.job_service)
        return service_class.__JOB_TYPE__
