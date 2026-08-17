#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
# This module is part of Artanis Enterprise Platform and is released under
# the Apache-2.0 License: https://www.apache.org/licenses/LICENSE-2.0
from faststream.rabbit import RabbitBroker
from taskiq.kicker import AsyncKicker

from artanis.component.redis import AsyncRedis, Redis
from artanis.config import Configuration
from artanis.events import EventBus, EventConcurrencyMode, EventHandlerCompletionMode, BaseEvent


async def configure_components(config: Configuration):
    await configure_redis(config)
    await configure_eventbus(config)
    await configure_message_queue(config)


async def configure_redis(config: Configuration):
    config.container.async_redis = await AsyncRedis.get_default_instance(create_instance=True)
    config.container.sync_redis = Redis.get_default_instance(create_instance=True)


async def configure_eventbus(config: Configuration):
    eventbus = EventBus(
        name='main_eventbus',
        event_concurrency=EventConcurrencyMode.PARALLEL,
        event_handler_completion=EventHandlerCompletionMode.FIRST,
        max_history_size=16,
        max_history_drop=True,
    )
    eventbus.on('*', propagate_event)
    config.container.eventbus = eventbus


async def configure_message_queue(config: Configuration):
    mq_uri = config.get_property_value(config.ARTANIS_MQ_CONNECTION, "")
    config.container.mq_broker = RabbitBroker(mq_uri)


async def propagate_event(event: BaseEvent) -> None:
    from artanis.taskiq.broker import event_broker
    await AsyncKicker(broker=event_broker, task_name="artanis_event", labels={}).kiq(
        event.__pydantic_serializer__.to_json(event),
    )
