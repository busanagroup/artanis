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

import weakref
from typing import Any, Optional, Type

from sqlalchemy.sql import select

from artanis.asgi.asgiendpoint import Descriptor
from artanis.config import Configuration
from artanis.sqlentity import Entity
from ecf.core import fakeapi
from ecf.core.ecfcmn import BaseController, SupportClass

ecNormal = 0
ecUpperCase = 1
ecLowerCase = 2


class MVCDescriptor(Descriptor):
    fields: list

    def get_field_list(self):
        return [name for name, _ in self.fields]

    def get_field_by_name(self, field: str) -> MVCFieldInfo | None:
        result = None
        for name, prop in self.fields:
            if name == field:
                result = prop()
                break
        return result

    def get_field_dict(self):
        return dict([(name, prop()) for name, prop in self.fields])

    def get_fields(self):
        return [prop() for _, prop in self.fields]


def duck_type_collection(specimen, default=None):
    """Given an instance or class, guess if it is or is acting as one of
    the basic collection types: list, set and dict.  If the __emulates__
    property is present, return that preferentially.
    """

    isa = isinstance(specimen, type) and issubclass or isinstance
    if isa(specimen, list):
        return list
    elif isa(specimen, set):
        return set
    elif isa(specimen, dict):
        return dict

    if hasattr(specimen, 'append'):
        return list
    elif hasattr(specimen, 'add'):
        return set
    elif hasattr(specimen, 'set'):
        return dict
    else:
        return default


def getmembers(object, predicate=None):
    base_props = []
    for key in dir(object):
        try:
            value = getattr(object, key)
        except AttributeError:
            continue
        if not predicate or predicate(value):
            base_props.append((key, value))
    return base_props


class MVCFieldInfo:  # type: ignore[misc]

    def __init__(self, field_type: Any, **kwargs):
        self.name: str
        self.type: Any = field_type
        self.label: str = kwargs.pop('label', None)
        self.required = kwargs.pop('required', False)
        self.enabled = kwargs.pop('enabled', True)
        self.visible = kwargs.pop('visible', True)
        self.readonly = kwargs.pop('readonly', False)
        self.synchronized = kwargs.pop('synchronized', False)
        self.browseable = kwargs.pop('browseable', False)
        self.charcase = kwargs.pop('charcase', ecNormal)
        self.updatable = kwargs.pop('updatable', True)
        self.savestate = kwargs.pop('savestate', True)
        self.autosync = kwargs.pop('autosync', False)
        self.default = kwargs.pop('default', None)
        self.choices = {}
        choice = kwargs.pop('choices', {})
        choice_type = duck_type_collection(choice)
        if choice and (choice_type == list or choice == tuple):
            for itval in choice:
                self.choices[itval] = itval
        else:
            if choice_type == dict:
                self.choices = choice.copy()
        self.field_no = 0
        self.kwargs = kwargs

    def attach(self, name: str, counter: int):
        self.name = name
        self.field_no = counter

    def field_info(self):
        return dict(name=self.name, type=self.type.get_dbapi_type(fakeapi), label=self.label, required=self.required,
                    enabled=self.enabled,
                    visible=self.visible, readonly=self.readonly, synchronized=self.synchronized,
                    browseable=self.browseable, charcase=self.charcase, updatable=self.updatable,
                    savestate=self.savestate,
                    autosync=self.autosync, choices=self.choices, **self.kwargs)


def MVCField(
        type: Any,
        label: str | None = None,
        required: bool = False,
        enabled: bool = True,
        visible: bool = True,
        readonly: bool = False,
        synchronized: bool = False,
        browseable: bool = False,
        charcase: int = ecNormal,
        updatable: bool = True,
        savestate: bool = True,
        autosync: bool = False,
        default: Any = None) -> MVCFieldInfo:
    return MVCFieldInfo(
        type,
        label=label,
        required=required,
        enabled=enabled,
        visible=visible,
        readonly=readonly,
        synchronized=synchronized,
        browseable=browseable,
        charcase=charcase,
        updatable=updatable,
        savestate=savestate,
        autosync=autosync,
        default=default
    )


class MVCModelBinder(SupportClass):
    def __init__(self, model: Optional[Type[Entity] | str], updatable: bool = True):
        self.model: Type[Entity] | None = self.get_entity(model) if isinstance(model, str) else model
        self.tablename = self.model.__tablename__
        self.updatable = updatable
        self.parent: weakref.ReferenceType[MVCBaseService] | None = None

    def set_parent(self, parent: MVCBaseService):
        self.parent = weakref.ref(parent)

    async def get_data_list(self, fields: list[str], offset: int, limit: int) -> list[dict]:
        if self.model is None:
            return []

        parent = self.parent() if self.parent else None
        descriptor_fields = parent.descriptor.get_field_list() if parent else []

        model_fields = set(self.model.get_field_names())
        allowed = set(descriptor_fields) & model_fields
        if fields:
            allowed &= set(fields)

        if not allowed:
            return []

        ordered_fields = [f for f in descriptor_fields if f in allowed]
        columns = [self.model.__table__.columns[f] for f in ordered_fields]

        session = self.get_session()
        stmt = select(*columns).offset(offset).limit(limit)
        result = await session.execute(stmt)
        rows = result.fetchall()
        return [dict(zip(ordered_fields, row)) for row in rows]






class MVCBaseService(BaseController):
    __config: Configuration
    descriptor = MVCDescriptor

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__config = Configuration.get_default_instance(create_instance=False)
        field_counter: int = 0
        cls.descriptor.fields = [(name, weakref.ref(attr)) for name, attr in cls.__dict__.items()
                                 if isinstance(attr, MVCFieldInfo)]
        for name, prop in cls.descriptor.fields:
            field = prop()
            field.attach(name, field_counter)
            field_counter += 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.has_model_binder():
            self.model_binder.set_parent(self)

    @classmethod
    def has_model_binder(cls) -> bool:
        return hasattr(cls, 'model_binder') and cls.model_binder is not None


class MVCService(MVCBaseService):
    description: str
