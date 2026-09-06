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
from artanis.events.cloudevents.event import CloudEvent

EVENTBUS_ATTR = ['event_blocks_parent_completion', 'event_completed_at', 'event_concurrency', 'event_created_at',
                 'event_emitted_by_handler_id', 'event_handler_completion', 'event_handler_concurrency',
                 'event_handler_slow_timeout', 'event_handler_timeout', 'event_id', 'event_parent_id', 'event_path',
                 'event_pending_bus_count', 'event_result_type', 'event_slow_timeout', 'event_started_at',
                 'event_status', 'event_timeout', 'event_type', 'event_version', 'event_results']
EVENTBUS_MAPPING = {'event_id': 'id',
                    'event_type': 'type',
                    'event_path': 'source',
                    'event_created_at': 'time',}
LAMBDA_MAPPING = {'time': lambda x: dt.datetime.fromisoformat(x) if isinstance(x, str) else x,
                  'source': lambda x: x[0] if isinstance(x, list) else str(x),}



def to_cloudevents(event: dict) -> CloudEvent:
    """Convert a dictionary to a CloudEvent format.

    :param event: The input event dictionary.
    :return: A CloudEvent object.
    """
    global EVENTBUS_ATTR, EVENTBUS_MAPPING, LAMBDA_MAPPING

    attributes = dict(datacontenttype='application/json')
    for key in EVENTBUS_ATTR:
        if key in EVENTBUS_MAPPING:
            cloudevent_key = EVENTBUS_MAPPING[key]
            attributes[cloudevent_key] = event[key] \
                if cloudevent_key not in LAMBDA_MAPPING \
                else LAMBDA_MAPPING[cloudevent_key](event[key])
        event.pop(key)
    return CloudEvent(attributes=attributes, data=event)


