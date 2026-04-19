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
from __future__ import annotations

import datetime as dt
import sys
import traceback

from artanis.component.validators import validators
from artanis.sqlentity.sqlorm import Session
from artanis.taskiq.proxy import JobObjectProxy
from ecf.core.croniter import Croniter
from ecf.core.ecfcmn import BaseController
from ecf.core.jobsvc import JobAssignment, JOBSession, JobRunner


class IntService(BaseController):

    @classmethod
    async def proceed_cron_job(cls):
        efcron = cls.get_entity('efcron')
        cronobjs = await efcron.get_all_tasks(1)
        session = Session()
        for crobj in cronobjs:
            crstr = " ".join([crobj.crjbsch1, crobj.crjbsch2, crobj.crjbsch3, crobj.crjbsch4, crobj.crjbsch5])
            lastexec = None
            if crobj.crjbexdt not in [none, 0]:
                lxdt = dt.date.frominteger(crobj.crjbexdt)
                lxtm = dt.time.frominteger(crobj.crjbextm)
                lastexec = dt.datetime.combine(lxdt, lxtm)

            today = dt.datetime.now()
            if (lastexec is not None) and (lastexec <= today):
                # --- create job assignmnet ----
                job = JobAssignment()
                job.description = f"executing job {crobj.crjbjbcd}"
                job.service_name = crobj.crjbjprg
                job.job_service_name = crobj.crjbjbcd
                job.user_name = crobj.crjbrsus
                # ----
                tb_str = crobj.crjbjtbl.strip() if crobj.crjbjtbl else none
                if tb_str not in [None, '']:
                    tb_klass = cls.get_entity(tb_str)
                    if tb_klass:
                        filter_str = {crobj.crjbjfld: crobj.crjbjfva}
                        obj = tb_klass.query.filter_by(**filter_str).first()
                        if obj:
                            # --- register job ---
                            await job.assign_job()
                            # -----
                            if not session.is_active:
                                session.begin()
                            try:
                                setattr(obj, crobj.crjbjbld, job.job_id)
                                session.add(obj)
                                await session.commit()
                            except:
                                session.rollback()
                else:
                    # --- we don't use table, so just register the job ---
                    await job.assign_job()

            cronproc = Croniter(crstr)
            nextexec = cronproc.get_next(dt.datetime)
            while nextexec < today:
                nextexec = cronproc.get_next(dt.datetime)

            if lastexec != nextexec:
                if not session.is_active:
                    session.begin()
                try:
                    crobj.crjbexdt = nextexec.date().tointeger()
                    crobj.crjbextm = nextexec.time().tointeger()
                    session.add(crobj)
                    await session.commit()
                except:
                    await session.rollback()

    async def check_unproceeded_job(self):
        efjbls = self.get_entity('efjbls')
        objs = await efjbls.get_all_jobs(0)
        date_now = dt.datetime.now()
        for obj in objs:
            if (obj.jblsrpdt is not None) and (obj.jblsrpdt != 0):
                date_request = dt.date.frominteger(obj.jblsrpdt)
                date_span = date_now.date() - date_request
                if date_span >= dt.timedelta(0):
                    if (obj.jblsrptm is not None) and (obj.jblsrptm != 0):
                        time_request = dt.time.frominteger(obj.jblsrptm)
                        date_span = date_now.time() - time_request
                        if date_span >= dt.timedelta(0):
                            await JobRunner(self.get_request(), obj.jblsidnm)
                    else:
                        await JobRunner(self.get_request(), obj.jblsidnm)
            else:
                await JobRunner(self.get_request(), obj.jblsidnm)

    @classmethod
    async def update_job_status(cls, user_session: JOBSession, status, msg, info=None):
        efjbls = cls.get_entity('efjbls')
        efjbif = cls.get_entity('efjbif')
        obj = efjbls.query.filter_by(jblsidnm=user_session.job_id).first()
        program_name = None
        session = Session()
        if obj:
            if obj.jblsauus:
                user_session.user_name = obj.jblsauus
            program_name = obj.jblsprpg
            now = dt.datetime.now()
            obj.jblsprdt = now.date().tointeger() if obj.jblsprdt is None else obj.jblsprdt
            obj.jblsprtm = now.time().tointeger() if obj.jblsprtm is None else obj.jblsprtm
            obj.jblsupdt = now.date().tointeger()
            obj.jblsuptm = now.time().tointeger()
            obj.jblsprst = status
            obj.jblsprms = msg[:128] if msg and isinstance(msg, str) else msg
            session.add(obj)

        lob = None
        message = msg
        if info:
            message = '\n'.join(traceback.format_exception(*info))
        update_lob = (message is not None) and (message.strip != '')
        if update_lob:
            lob = efjbif.query.filter_by(jblxidnm=user_session.job_id).first()
        if lob:
            lob.jblxplms = message
            session.add(lob)

        if not session.is_active:
            session.begin()
        try:
            session.commit()
        except:
            session.rollback()
            raise
        return program_name

    @classmethod
    async def execute_job(cls, request, job_id: str):
        job_session = JOBSession(job_id)
        job_session.adapt_request(request)
        program_name = await cls.update_job_status(job_session, 10, None)
        validators.Assertion(messages={'assert': f"No JOB Processor defined for jobID={job_id}"}).to_python(
            program_name is not None)
        proxy = JobObjectProxy(request)
        try:
            await proxy.execute_job(job_session)
            await cls.update_job_status(job_session, 100, None)
        except Exception as exc:
            exc_info = sys.exc_info()
            await cls.update_job_status(job_session, 99, exc, exc_info)
            raise

    @classmethod
    async def get_user_password(cls, user_name: str):
        efusrs = cls.get_entity('efusrs')
        return await efusrs.get_user_password(user_name)

    @classmethod
    async def check_user_auth(cls, user_name: str, password: str):
        efusrs = cls.get_entity('efusrs')
        return await efusrs.check_user_auth(user_name, password)

    @classmethod
    async def check_user_activation(cls, user_name: str):
        efusrs = cls.get_entity('efusrs')
        return await efusrs.is_user_active(user_name)

    @classmethod
    async def change_user_password(cls, user_name: str, old_passwd: str, new_passwd: str):
        efusrs = cls.get_entity('efusrs')
        return await efusrs.change_user_password(user_name, old_passwd, new_passwd)

    @classmethod
    async def check_api_object(cls, user_name: str, obj_name: str):
        efuaob = cls.get_entity('efuaob')
        return await efuaob.check_api_object(user_name, obj_name)

    @classmethod
    async def verify_api_access(cls, user_name: str, obj_name: str):
        return await cls.verify_api_access(user_name, obj_name)

    @classmethod
    async def check_api_func(cls, user_name: str, obj_name: str, func_name: str, access_type: str):
        efuafn = cls.get_entity('efuafn')
        return await efuafn.check_api_func(user_name, obj_name, func_name, access_type)

    @classmethod
    async def get_user_group(cls, user_name: str):
        efugrp = cls.get_entity('efugrp')
        return await efugrp.get_user_group(user_name)

    @classmethod
    async def check_api_user_auth(cls, user_name: str, obj_name: str, func_name: str, access_type: str):
        res = await cls.check_api_object(user_name, obj_name)
        if res:
            res = await cls.check_api_func(user_name, obj_name, func_name, access_type)
        return res

    @classmethod
    async def check_api_auth(cls, user_name: str, obj_name: str, func_name: str, access_type: str):
        res = await cls.check_api_user_auth(user_name, obj_name, func_name, access_type)
        if not res:
            group_list = await cls.get_user_group(user_name)
            for group in group_list:
                res = await cls.check_api_user_auth(group, obj_name, func_name, access_type)
                if res:
                    break
        return res

    @classmethod
    async def verify_mvc_access(cls, user_name: str, obj_name: str, access_type: int):
        efumob = cls.get_entity('efumob')
        efmxob = cls.get_entity('efmxob')
        res = await efumob.verify_user_access(user_name, obj_name, access_type, False)
        if res:
            res = await efmxob.verify_user_access(user_name, obj_name, access_type, False)
        return res

    @classmethod
    async def check_mvc_auth(cls, user_name: str, obj_name: str, access_type: int):
        efumob = cls.get_entity('efumob')
        efmxob = cls.get_entity('efmxob')
        res = await efumob.check_public_access(obj_name, access_type)
        if res:
            res = await efmxob.check_user_access(user_name, obj_name, access_type)
        elif not res:
            grps = await cls.get_user_group(user_name)
            if grps:
                for grp in grps:
                    res = await efumob.check_user_access(grp, obj_name, access_type)
                    if res:
                        break
                if res:
                    for grp in grps:
                        res = await efmxob.check_user_access(grp, obj_name, access_type)
                        if not res:
                            break
        return res

    @classmethod
    async def verify_dm_access(cls, user_name: str, obj_name: str, access_type: int):
        efudob = cls.get_entity('efudob')
        return await efudob.verify_user_access(user_name, obj_name, access_type, False)

    @classmethod
    async def check_dm_auth(cls, user_name: str, obj_name: str, access_type: str):
        efudob = cls.get_entity('efudob')
        efugrp = cls.get_entity('efugrp')
        res = await efudob.check_public_access(obj_name, access_type)
        if not res:
            grps = await efugrp.get_user_group(user_name)
            for grp in grps:
                res = await efudob.check_user_access(grp, obj_name, access_type)
                if res:
                    break
        return res

    @classmethod
    async def check_rpc_auth(cls, user_name: str, service_name: str, method_name: str):
        efurob = cls.get_entity('efurob')
        efugrp = cls.get_entity('efugrp')
        res = await efurob.check_public_access(service_name, method_name)
        if not res:
            grps = await efugrp.get_user_group(user_name)
            if grps:
                for grp in grps:
                    res = await efurob.check_user_access(grp, service_name, method_name)
                    if res:
                        break
        return res

    @staticmethod
    def setup_app_panel(dict_val: dict):
        keys = ['first_name'] if 'first_name' in dict_val and dict_val['first_name'] \
            else ['user_name']
        keys.extend(['last_name', 'cmdvdvds'])
        data_lst = [dict_val[key] for key in keys if key in dict_val and dict_val[key]]
        dict_val['panel_title'] = " ".join(data_lst)

    @classmethod
    async def get_system_info(cls, user_name: str):
        efusrs = cls.get_entity('efusrs')
        mstcmp = cls.get_entity('mstcmp')
        cmpdiv = cls.get_entity('cmpdiv')
        retdict = {}
        usr = await efusrs.get(user_name)
        if usr:
            retdict['user_name'] = usr.efususid
            retdict['first_name'] = usr.efusfsnm
            retdict['last_name'] = usr.efuslsnm

            auditfields = ('aucd', 'auct', 'audt', 'autm', 'auus')

            if usr.efuscono:
                cmpobj = await mstcmp.get(usr.efuscono)
                if cmpobj:
                    for key, value in mstcmp.__dict__.items():
                        if isinstance(value, InstrumentedAttribute) and \
                                (key[4:] not in auditfields):
                            val = getattr(cmpobj, key, None)
                            retdict[key] = val
                mstdiv = await cmpdiv.get((usr.efuscono, usr.efusdvno))
                if mstdiv:
                    for key, value in cmpdiv.__dict__.items():
                        if isinstance(value, InstrumentedAttribute) and \
                                (key[4:] not in auditfields):
                            val = getattr(mstdiv, key, None)
                            retdict[key] = val
        cls.setup_app_panel(retdict)
        values = [(key, value) for key, value in retdict.items()]
        return tuple(values)

    async def change_user_cmp(self, user_name: str, user_cono: str, user_divi: str):
        proxy = self.get_bo_proxy()
        usrobj = proxy.get_object('usrobj')
        cmpobj = proxy.get_object('cmpobj')
        efuacd = self.get_entity('efuacd')
        efusrs = self.get_entity('efusrs')
        usr = await efusrs.get(user_name)
        divi = await cmpobj.get_division(user_cono, user_divi)
        validators.NotEmpty(messages={'empty': 'user name could not be found'}).to_python(usr)
        uacd = await efuacd.get((user_name, user_cono, user_divi))
        validators.NotEmpty(messages={'empty': 'Access to specified company and division is denied'}) \
            .to_python(uacd)
        usr.efuscono = divi[0]
        usr.efusconm = divi[1]
        usr.efusdvno = divi[2]
        usr.efusdvnm = divi[3]
        self.set_audit_fields(usr, user_name)
        session = Session()
        if not session.is_active:
            session.begin()
        try:
            session.add(usr)
            session.commit()
            usrobj.update_user_cache(usr)
        except:
            session.rollback()
            raise

