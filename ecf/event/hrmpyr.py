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
from ecf.api.cmnsvc import SalaryCalculationEvent, SalaryRollbackEvent
from ecf.core.eventsvc import EventHandler, on_event


class hrmpyr(EventHandler, event_type="com.busanagroup.artanis.hrms.payroll"):

    @on_event(event_type="salary.calculated")
    def handle_salary_calculated(self, event: SalaryCalculationEvent):
        print(f"from handle_salary_calculated, event: {event.event_type} message: {event.message}")

    @on_event(event_type=[
        "salary.calculated",
        "salary.rollback",
    ])
    def handle_other_salary_rollback(self, event: SalaryRollbackEvent):
        print(f"from handle_other_salary_rollback, event: {event.event_type} message: {event.message}")

