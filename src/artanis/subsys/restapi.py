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

from artanis.subsys.asgisubsys import ASGISubsystem
from artanis.subsys.asgisubsys import ASGIWorkerFactory
from artanis.config import Configuration


class APIWorkerFactory(ASGIWorkerFactory):
    worker_name = 'api_worker'


class APISubsystem(ASGISubsystem):
    config_service_enabled = Configuration.ARTANIS_API_ENABLED
    config_bind_type = Configuration.ARTANIS_API_BINDTYPE
    config_bind = Configuration.ARTANIS_API_BIND
    config_process_instances = Configuration.ARTANIS_API_INSTANCES

    class_factory = APIWorkerFactory
    subsystem_name = 'apisub'

    def do_configure(self):
        super().do_configure()
        self.asgi_config.application_path = 'artanis.asgi.restapi:app'
