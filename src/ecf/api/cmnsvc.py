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
from starlette.responses import JSONResponse

from artanis.asgi.asgiendpoint import published
from artanis.component.queue.krbridge import MessageNotifier, MessageCommand
from artanis.events import BaseEvent
from ecf.core.apisvc import *


class SalaryCalculationEvent(BaseEvent, event_type="com.busanagroup.artanis.hrms.payroll.salary.calculated"):
    message: dict

class SalaryRollbackEvent(SalaryCalculationEvent, event_type="com.busanagroup.artanis.hrms.payroll.salary.rollback"):...


class cmnsvc(APIService):
    description = 'Common Service API'

    @published(path='/userinfo', methods=['GET'])
    async def get_user_info(self):
        message = {'hello': 'world'}
        # await self.eventbus.emit(SalaryCalculationEvent(message=message))
        # await self.eventbus.emit(SalaryRollbackEvent(message=message))
        event = MessageNotifier(module='TASM', submodule='HREMAS')
        await event.notify('HREMAS_UPDATE', cono=600, emid=200305184)

        command = MessageCommand(module='FASM', submodule='CAPEX')
        await command.doInsertHSCode(cono=600, dvno="USFG", hscode=0, frdt=None)
        return JSONResponse({'hello': 'world'})

