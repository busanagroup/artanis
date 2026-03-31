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

import asyncio
import types
import copy
from functools import cache
from dataclasses import dataclass, asdict
from typing import Optional, Type, Callable, Coroutine, Any

from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql._typing import _TypeEngineArgument, _T
from sqlalchemy.types import *

import artanis.sqlentity as ecfentity
from artanis.abc.classprops import classproperty
from artanis.asgi.endpoints.base import BaseDescriptor
from artanis.config import Configuration
from artanis.component.validators import validators
from artanis.sqlentity import Entity, Session

from ecf.core import ifakeapi, fakeapi
from ecf.core.ecfcmn import BaseController, BaseUserSession, ECFObject, SupportClass, ObjectProxy
from ecf.core.sqladbapi import SQLATypeHelper
from ecf.core.dataset import VirtualDataset

MVCTypeParam = 1
MVCTypeList = 2
MVCTypeField = 4

MVCExecUnknown = 0
MVCExecShow = 1
MVCExecCopy = 2
MVCExecAppend = 3
MVCExecEdit = 4
MVCExecDelete = 5
MVCExecSelect = 6

MVCFuncSelect = 0
MVCFuncNew = 1
MVCFuncOpen = 2
MVCFuncShow = 3
MVCFuncCopy = 4
MVCFuncDelete = 5

ecNormal = 0
ecUpperCase = 1
ecLowerCase = 2

EF_CAT_RELATED = 0
EF_CAT_FUNCTION = 1


class MVCSession(BaseUserSession):
    __VERSION__: int = 1

    def __init__(self, controller):
        self.field_defs = ECFObject()
        self.page_defs = getattr(controller, '_pages', ())
        self.supported_funcs = getattr(controller, '_supported_functions', ())
        self.exec_type = MVCExecUnknown
        self.program = controller.descriptor.name
        self.page = None
        self.ext_functions = None
        self.select_function = None
        self.print_id = None
        self.command_text = MVCCommandText()
        self.enabled_functions = []
        self.container = None
        if controller.has_request:
            request = controller.get_request()
            self.cookies['user_name'] = request.user.username if hasattr(request.user, 'username') else None

        # copy default field properties
        for field_name in controller.descriptor.fields:
            field = getattr(controller.__class__, field_name)
            if not hasattr(self.field_defs, field.properties.name):
                setattr(self.field_defs, field.properties.name, MVCFieldProperties(choices={}))
            aprops = getattr(self.field_defs, field.properties.name)
            aprops.copy_properties(field.properties)
            aprops.tlabel = aprops.label

        self.__entry_dataset = None
        self.__list_dataset = None
        self.__param_dataset = None

    @property
    def entry_dataset(self) -> VirtualDataset:
        if not self.__entry_dataset:
            self.__entry_dataset = VirtualDataset()
            self.__param_dataset.bind_dataset(self.get_field_defs(), MVCTypeField)
        return self.__entry_dataset

    @property
    def param_dataset(self) -> VirtualDataset:
        if not self.__param_dataset:
            self.__param_dataset = VirtualDataset()
            self.__param_dataset.bind_dataset(self.get_field_defs(), MVCTypeParam)
        return self.__param_dataset

    @property
    def list_dataset(self) -> VirtualDataset:
        if not self.__list_dataset:
            self.__list_dataset = VirtualDataset()
            self.__param_dataset.bind_dataset(self.get_field_defs(), MVCTypeList)
        return self.__list_dataset

    def get_dataset(self, dsname):
        aval = dsname.lower()
        return self.entry_dataset if aval == 'entry' else \
            self.param_dataset if aval == 'list' else \
                self.list_dataset if aval == 'params' else None

    def get_field_property(self, field_name: str):
        return getattr(self.field_defs, field_name, None) \
            if hasattr(self.field_defs, field_name) else None

    def get_fields(self):
        field_dict = self.field_defs.__dict__
        return [(name, attr) for name, attr in field_dict.items() if isinstance(attr, MVCFieldProperties)]

    @cache
    def get_field_defs(self):
        return [field.get_field_def() for name, field in self.get_fields()]

    def set_fields(self, lst_field, lst_props, value):
        for fld in lst_field:
            for prop in lst_props:
                setattr(getattr(self.field_defs, fld), prop, value)

    def get_field_list(self, field_type: int):
        return [attr[1] for attr in self.get_field_defs() if (attr[3] | field_type) == attr[3]]

    def get_updatable_fields(self, field_type: int):
        return [attr[1] for attr in self.get_field_defs() if ((attr[3] | field_type) == attr[3]) and (attr[17] is True)]

    def get_ext_functions(self):
        if self.ext_functions is None:
            return []
        return [func.get_ext_function() for func in self.ext_functions] \
            if isinstance(self.ext_functions, (tuple, list)) \
            else [self.ext_functions.get_ext_function()]

    def get_select_function(self):
        return self.select_function.get_ext_function() if self.select_function else None

    @staticmethod
    def __new_ext_function__():
        return MVCExtFunction('', '', '')

    def copy_session(self, other):
        self.exec_type = copy.deepcopy(other.exec_type)
        self.cookies = copy.deepcopy(other.cookies)
        self.__param_dataset = other.paramDataset
        self.__entry_dataset = other.entryDataset
        self.__list_dataset = other.listDataset
        self.program = copy.deepcopy(other.program)
        self.page = copy.deepcopy(other.page)
        self.supported_funcs = copy.deepcopy(other.supported_funcs)
        self.command_text = copy.deepcopy(other.command_text)
        self.print_id = copy.deepcopy(other.printID)
        sorted_fields = other.get_fields()
        for name, field in sorted_fields:
            if not hasattr(self.field_defs, name):
                setattr(self.field_defs, name, MVCFieldProperties(choices={}))
            getattr(self.field_defs, name).copy_properties(field)
        return self

    def set_enabled(self, fields, value=True):
        if isinstance(fields, str):
            if fields == '*':
                sorted_fields = self.get_fields()
                for name, field in sorted_fields:
                    field.enabled = value
                    setattr(self.field_defs, name, field)
            else:
                flist = fields.split(";")
                for field in flist:
                    obj = getattr(self.field_defs, field, None)
                    if obj:
                        obj.enabled = value
                        setattr(self.field_defs, field, obj)
        elif isinstance(fields, (list, tuple)):
            for field in fields:
                obj = getattr(self.field_defs, field, None)
                if obj:
                    obj.enabled = value
                    setattr(self.field_defs, field, obj)

    def serialize(self):
        field_defs = [field.serialize() for name, field in self.get_fields()]
        return [self.__VERSION__,
                self.program,
                self.page,
                self.command_text.serialize(),
                [(key, value) for key, value in self.cookies.items()],
                field_defs,
                self.exec_type,
                self.supported_funcs,
                self.get_ext_functions() if self.container is None else self.container[0],
                self.get_select_function() if self.container is None else self.container[1]]

    def deserialize(self, session_info: list):
        validators.Assertion(messages={"assert": "Not a valid MVCSessionData"}).to_python(len(session_info) == 10)
        validators.Assertion(messages={"assert": "Not a valid MVCSessionData record version"}).to_python(
            session_info[0] == self.__VERSION__)
        self.container = session_info[8:][:2]
        self.__param_dataset = None
        self.__entry_dataset = None
        self.__list_dataset = None

    def load_dataset(self, datasets: list):
        self.param_dataset.from_array(datasets[0])
        self.list_dataset.from_array(datasets[1])
        self.entry_dataset.from_array(datasets[2])


class MVCCommandText(object):
    def __init__(self):
        self.params = dict()
        self.command_type = 'INTERNAL'
        self.command = None

    def exec_method(self, method):
        if callable(method):
            self.command = method.__name__
            self.command_type = 'INTERNAL'

    def exec_view(self, view):
        self.command = view
        self.command_type = 'VIEW'

    def set_param(self, key, value):
        self.params[key] = value

    def get_param(self, key):
        return self.params[key]

    def get_params(self):
        return sorted([(key, value) for key, value in self.params.items()],
                      key=lambda i: i[1])

    def copy_from(self, other_session: MVCCommandText):
        self.params.update(other_session.params)
        self.command_type = other_session.command_type
        self.command = other_session.command
        return self

    def get_command_text(self):
        tmp_param = self.get_params()
        return self.command_type, str(self.command), tmp_param

    def set_command_text(self, cmd_text):
        self.command_type, self.command, tmp_param = cmd_text
        self.params = dict(tmp_param)

    def serialize(self):
        return [self.command_type, self.command, [(key, value) for key, value in self.params.items()]]

    def deserialize(self, info):
        self.command_type, self.command, params = info
        self.params.update(params)


class MVCLookupDef(object):
    """
    Provide Lookup definition into a specific program for an entry field
    example:
      ret = MVCLookupDef('CMN100','CMCPCONO',
              params = {'PARAMFLD':'%v:some value'
                  'PARAMFLD':'%f:SRCFIELD'}
              extassign = {'SOMEFIELD':'%v:some value'
                  'OTHERFIELD':'%f:SRCFIELD'
                })
    """

    def __init__(self, svcname, retfield, **kwargs):
        self.params = kwargs.pop('params', {})
        self.svcname = svcname
        self.retfield = retfield
        self.extassignment = kwargs.pop('extassign', {})

    def setup(self, svcname, retfield, **kwargs):
        self.svcname = svcname
        self.retfield = retfield
        self.params = kwargs.pop('params', {})
        self.extassignment = kwargs.pop('extassign', {})

    def get_params(self):
        return sorted([(key, value) for key, value in self.params.items()],
                      key=lambda i: i[1])

    def get_ext_assigment(self):
        return sorted([(key, value) for key, value in self.extassignment.items()],
                      key=lambda i: i[1])


class MVCExtFunction(object):
    def __init__(self, func_id, label, method, dynamic=False, **kwargs):
        self.params = kwargs.pop('params', {})
        self.auto_select = kwargs.pop('autoSelect', False)
        self.confirm_message = kwargs.pop('confirmMessage', None)
        func_type = kwargs.pop('functionType', None)
        self.func_id = func_id
        self.label = label
        self.dynamic = dynamic
        self.command_type = None
        self.command_text = None
        self.set_method(method, func_type)
        self.function_name = None

    def set_method(self, method, func_type=None):
        if func_type is None:
            if callable(method):
                self.command_type = 'INTERNAL'
                self.command_text = method.__name__
            else:
                self.command_type = 'VIEW'
                self.command_text = method
        elif func_type == EF_CAT_FUNCTION:
            self.command_type = 'INTERNAL'
            if callable(method):
                self.command_text = method.__name__
            else:
                self.command_text = method
        elif func_type == EF_CAT_RELATED:
            self.command_type = 'VIEW'
            if callable(method):
                self.command_text = method.__name__
            else:
                self.command_text = method

    def get_params(self):
        return tuple(sorted([(key, value) for key, value in self.params.items()],
                            key=lambda i: i[1]))

    def get_ext_function(self):
        tmp_param = self.get_params()
        return (self.label, self.command_type, self.dynamic, self.auto_select,
                self.command_text, self.confirm_message, tmp_param)


@dataclass
class MVCFieldProperties:
    choices: dict | None
    field_no: int = 0
    data_type: object = None
    field_type: int | None = None
    name: str | None = None
    label: str | None = None
    tlabel: str | None = None
    required: bool = False
    enabled: bool = True
    visible: bool = True
    readOnly: bool = False
    updateable: bool = True
    primaryKey: bool = False
    kwargs: dict | None = None
    synchronized: bool = False
    browseable: bool = False
    charcase: int = ecNormal
    savestate: bool = True
    autosync: bool = False

    def copy_properties(self, props: MVCFieldProperties):
        for key, value in asdict(props).items():
            setattr(self, key, value)

    def get_field_def(self) -> tuple:
        tpchoice = sorted([(key, value) for key, value in self.choices.items()], key=lambda i: i[1])
        _len = getattr(self.data_type, 'length', 0)
        _prec = getattr(self.data_type, 'precision', 0)
        _scale = getattr(self.data_type, 'scale', 0)
        _len = _len if _len is not None else 0
        _prec = _prec if _prec is not None else 0
        _scale = _scale if _scale is not None else 0
        _data_type = SQLATypeHelper.get_ecf_type(self.data_type, fakeapi)
        return (self.field_no,
                self.name,
                self.tlabel,
                self.field_type,
                _data_type,
                _len,
                _prec,
                _scale,
                self.primaryKey,
                self.required,
                self.enabled,
                self.visible,
                self.readOnly,
                tuple(tpchoice),
                self.synchronized,
                self.browseable,
                self.charcase,
                self.updateable,
                self.savestate)

    def serialize(self):
        tpchoice = sorted([(key, value) for key, value in self.choices.items()], key=lambda i: i[1])
        _len = getattr(self.data_type, 'length', 0)
        _prec = getattr(self.data_type, 'precision', 0)
        _scale = getattr(self.data_type, 'scale', 0)
        _len = _len if _len is not None else 0
        _prec = _prec if _prec is not None else 0
        _scale = _scale if _scale is not None else 0
        _data_type = SQLATypeHelper.get_ecf_type(self.data_type, fakeapi)
        return (self.field_no,
                self.name,
                self.tlabel,
                self.field_type,
                _data_type,
                _len,
                _prec,
                _scale,
                self.primaryKey,
                self.required,
                self.enabled,
                self.visible,
                self.readOnly,
                tuple(tpchoice),
                self.synchronized,
                self.browseable,
                self.charcase)


class MVCField:

    def __init__(self, field_type: int, value_type: Optional[_TypeEngineArgument[_T]], **kwargs):
        self.properties = MVCFieldProperties(choices={})
        self.properties.data_type = value_type
        self.properties.field_type = field_type
        self.properties.label = kwargs.pop('label', None)
        self.properties.required = kwargs.pop('required', False)
        self.properties.enabled = kwargs.pop('enabled', True)
        self.properties.visible = kwargs.pop('visible', True)
        self.properties.readOnly = kwargs.pop('readOnly', False)
        self.properties.readOnly = kwargs.pop('readonly', self.properties.readOnly)
        self.properties.synchronized = kwargs.pop('synchronized', False)
        self.properties.browseable = kwargs.pop('browseable', False)
        self.properties.charcase = kwargs.pop('charcase', ecNormal)
        self.properties.updateable = kwargs.pop('updateable', True)
        self.properties.savestate = kwargs.pop('savestate', True)
        self.properties.autosync = kwargs.pop('autosync', False)
        self.properties.primaryKey = kwargs.pop('primaryKey', False)
        self.properties.kwargs = kwargs
        choice = kwargs.pop('choices', {})
        if not choice:
            return
        if isinstance(choice, list) or isinstance(choice, tuple):
            for value in choice:
                self.properties.choices[value] = value
        else:
            self.properties.choices = choice.copy()


class MVCModelBinder(SupportClass):
    def __init__(self, model: Optional[Type[Entity] | types.ModuleType], updatable: bool = True):
        self.model = self.get_entity(model) if isinstance(model, str) else model
        self.tablename = model.__tablename__
        self.updatable = updatable

    async def prepare_session(self, controller, mvcsession: MVCSession, initview_method: Callable):
        proxy = ObjectProxy(controller.get_request())
        usrobj = proxy.get_object('usrobj')
        sysobj = proxy.get_object('sysobj')
        user_name = mvcsession if isinstance(mvcsession, str) else mvcsession.user_name
        info = await usrobj.retrieve_user_info(user_name)
        cono = info[2] if info[2] is not None else ''
        mvcsession.cookies['cono'] = cono
        if self.model is not None:
            key_params = mvcsession.get_field_list(MVCTypeParam)
            if len(key_params) > 0:
                _dict = await sysobj.get_program_vars(cono, mvcsession)
                param_dataset = mvcsession.param_dataset
                if not param_dataset.active:
                    param_dataset.open()
                if len(_dict) > 0 and param_dataset.active:
                    if param_dataset.record_count != 0:
                        param_dataset.edit()
                    else:
                        param_dataset.append()
                    param_dataset.set_value_dict(_dict)
                    param_dataset.post()
        return await initview_method(mvcsession)

    @staticmethod
    def initialize_data(mvcsession: MVCSession):
        keyparams = mvcsession.get_field_list(MVCTypeParam)
        keyfields = mvcsession.get_field_list(MVCTypeField)
        fields = dict([(key, None) for key in keyfields])
        if len(keyparams) > 0:
            params = mvcsession.param_dataset.field_as_dict_ext()
            fields.update([(key, params[key]) for key in keyparams if key in keyfields])
            mvcsession.entry_dataset.adjust_record(fields)

    @staticmethod
    def init_copy_data(mvcsession: MVCSession):
        keyparams = mvcsession.get_field_list(MVCTypeParam)
        if len(keyparams) == 0:
            keyfields = mvcsession.get_field_list(MVCTypeField)
            params = mvcsession.param_dataset.field_as_dict_ext()
            fields = dict([(key, params[key]) for key in keyparams if key in keyfields])
            mvcsession.entry_dataset.adjust_record(fields)

    def set_audit_field(self, obj: object, mvcsession: MVCSession):
        ecfentity.set_audit_fields(obj, mvcsession)

    def get_user_name(self, user_session):
        return ecfentity.get_user_name(user_session)

    def get_fields(self, pk_type: int = 0):
        return [] if not self.model else [field.name for field in self.model.__dict__.values() if (pk_type == 0) \
                                          or ((pk_type == 0) and field.primary_key) \
                                          or ((pk_type == 1) and (not field.primary_key)) \
                                          or ((pk_type == 2) and (field.primary_key or field.nullable))]

    def get_pk_fields(self):
        return self.get_fields(1)

    async def get_record(self, sender, mvcsession: MVCSession):
        if (self.model is not None) and (mvcsession.exec_type != MVCExecAppend):
            fields = mvcsession.list_dataset.field_as_dict_ext()
            pkfields = self.get_pk_fields()
            try:
                values = [fields[pk] for pk in pkfields]
            except:
                raise Exception("Some of required primary key field is not included as list type field")
            obj = await self.model.get(tuple(values))
            if obj:
                fields = mvcsession.get_field_list(MVCTypeField)
                if mvcsession.exec_type == MVCExecCopy:
                    pfields = [fld for fld in fields if (fld not in pkfields)]
                    fields = pfields
                fieldlist = ";".join(fields)
                mvcsession, obj = sender.before_retrieve_data(mvcsession, obj)
                mvcsession.entry_dataset.copy_from_orm(fieldlist, fieldlist, obj)
                if mvcsession.exec_type == MVCExecEdit:
                    ecfentity.save_timestamp(mvcsession.cookies, obj)
                    fields = self.get_fields(1)
                    for field in fields:
                        if getattr(mvcsession.field_defs, field, None) is not None:
                            getattr(mvcsession.field_defs, field).enabled = False
                if mvcsession.exec_type == MVCExecCopy:
                    self.init_copy_data(mvcsession)
                mvcsession, obj = await sender._after_retrieve_data(mvcsession, obj)
            else:
                raise Exception("record could not be found")
        elif self.model and (mvcsession.exec_type == MVCExecAppend):
            await sender.initialize_data(mvcsession)
            await sender.after_init_data(mvcsession)
            await sender.perform_synchronize_data(mvcsession, MVCTypeField)

    async def set_record(self, sender, mvcsession: MVCSession):
        ...


class MVCDescriptor(BaseDescriptor):
    fields: list

    def __init__(self):
        self.fields = []


class MVCBaseController(BaseController):
    __config = Configuration.get_default_instance(create_instance=False)
    __descriptor = MVCDescriptor()

    def has_model_binder(self):
        return getattr(self, '_model_binder', None) is not None

    async def perform_init_view(self, mvcsession):
        _binder = getattr(self, '_model_binder', None)
        mvcsession = await self.init_view(mvcsession) if _binder is None \
            else await _binder.prepare_session(self, mvcsession, self.init_view)
        return mvcsession

    async def init_view(self, mvcsession):
        return mvcsession

    def init_program_exec(self, mvcsession, extfunc):
        return extfunc

    def open_view(self, mvcsession):
        _binder = getattr(self, '_model_binder', None)
        if _binder is not None:
            _binder.get_object_list(self, mvcsession)
        return mvcsession

    def retrieve_data(self, mvcsession):
        _binder = getattr(self, '_model_binder', None)
        if _binder is not None:
            _binder.get_record(self, mvcsession)
        return mvcsession

    def _get_field_list(self, mvcsession, ftype):
        return [attr[1] for attr in mvcsession.get_field_defs() \
                if ((attr[3] | ftype) == attr[3])]

    def perform_synchronize_data(self, mvcsession, field_type=MVCTypeField):
        fields = self._get_field_list(mvcsession, field_type)
        for field in fields:
            _field = getattr(mvcsession.fieldDefs, field, None)
            if (_field is not None) and (_field.synchronized == True) \
                    and (_field.autosync == True):
                self.synchronize_data(mvcsession, field, MVCTypeField)

    def synchronize_data(self, mvcsession, field_name, field_type):
        return mvcsession

    def post_data(self, mvcsession):
        _binder = getattr(self, '_model_binder', None)
        if _binder is not None:
            _binder.set_record(self, mvcsession)
        return mvcsession

    def print_data(self, mvcsession):
        return getattr(self, '_print_id', None) \
            if mvcsession.printID is None else mvcsession.printID

    def validate_data(self, mvcsession):
        return mvcsession

    def before_retrieve_data(self, mvcsession, obj):
        return mvcsession, obj

    def validate_posting_status(self, mvcsession, obj):
        return True

    def after_retrieve_data(self, mvcsession, obj):
        return mvcsession, obj

    def _after_retrieve_data(self, mvcsession, obj):
        if mvcsession.execType not in [MVCExecShow, MVCExecCopy]:
            value_to_check = self.validate_posting_status(mvcsession, obj)
            validators.Assertion(
                messages={'assert': 'The transaction has already been posted, cannot modify. '
                                    'Please consider to use SHOW function instead'}
            ).to_python(value_to_check == True)
        return self.after_retrieve_data(mvcsession, obj)

    def before_append_data(self, mvcsession, obj):
        return mvcsession, obj

    def before_copy_data(self, mvcsession, obj):
        return mvcsession, obj

    def before_edit_data(self, mvcsession, obj):
        return mvcsession, obj

    def before_delete_data(self, mvcsession, obj):
        return mvcsession, obj

    def before_post_data(self, mvcsession, obj):
        return mvcsession, obj

    def _before_post_data(self, mvcsession, obj):
        if mvcsession.execType == MVCExecDelete:
            value_to_check = self.validate_posting_status(mvcsession, obj)
            validators.Assertion(
                messages={'assert': 'The transaction has already been posted, cannot delete. ' \
                                    'Please consider to use SHOW function instead'}
            ).to_python(value_to_check == True)

        mvcsession, obj = self.before_post_data(mvcsession, obj)
        if mvcsession.execType == MVCExecCopy:
            return self.before_copy_data(mvcsession, obj)
        elif mvcsession.execType == MVCExecAppend:
            return self.before_append_data(mvcsession, obj)
        elif mvcsession.execType == MVCExecEdit:
            return self.before_edit_data(mvcsession, obj)
        elif mvcsession.execType == MVCExecDelete:
            return self.before_delete_data(mvcsession, obj)
        return mvcsession, obj

    def before_commit_data(self, mvcsession, obj):
        return mvcsession, obj

    def after_append_data(self, mvcsession, obj):
        return mvcsession, obj

    def after_copy_data(self, mvcsession, obj):
        return mvcsession, obj

    def after_edit_data(self, mvcsession, obj):
        return mvcsession, obj

    def after_delete_data(self, mvcsession, obj):
        return mvcsession, obj

    def after_post_data(self, mvcsession, obj):
        return mvcsession, obj

    def _after_post_data(self, mvcsession, obj):
        mvcsession, obj = self.after_post_data(mvcsession, obj)
        if mvcsession.execType == MVCExecCopy:
            return self.after_copy_data(mvcsession, obj)
        elif mvcsession.execType == MVCExecAppend:
            return self.after_append_data(mvcsession, obj)
        elif mvcsession.execType == MVCExecEdit:
            return self.after_edit_data(mvcsession, obj)
        elif mvcsession.execType == MVCExecDelete:
            return self.after_delete_data(mvcsession, obj)
        return mvcsession, obj

    def initialize_data(self, mvcsession):
        if self.has_model_binder():
            _binder = getattr(self, '_model_binder', None)
            _binder.initialize_data(mvcsession)
        return mvcsession

    def after_init_data(self, mvcsession):
        return mvcsession

    def initialize_query(self, mvcsession, model):
        _binder = getattr(self, '_model_binder', None)
        query = _binder.getQuery(self, mvcsession) if _binder is not None else model.query
        return mvcsession, query

    def initialize_param(self, mvcsession, query):
        return query

    def finalize_view(self, mvcsession):
        return mvcsession

    def lookup_view(self, mvcsession, fieldName):
        return MVCLookupDef('', '')

    async def after_get_session(self, mvcsession, user_name):
        return mvcsession

    @classmethod
    def create_instance(cls, pool, module):
        obj = object.__new__(cls)
        obj.__init__()
        return obj

    @classmethod
    def instantiate(cls):
        obj = object.__new__(cls)
        obj.__init__()
        return obj

    def get_field_info(self, field_name):
        for field in self.descriptor.fields:
            if field.properties.name == field_name:
                return field
        return None

    @classproperty
    def descriptor(cls):
        return cls.__descriptor

    def __getfielddefs__(self):
        ret = list()
        _binder = getattr(self, '_model_binder', None)
        try:
            for field in self.descriptor.fields:
                tpchoice = [(key, value) for key, value in field.properties.choices.items()]
                label = field.properties.tlabel
                if (field.properties.label is None) and (_binder is not None):
                    field = getattr(_binder.model, field.properties.name, None)
                    if field and isinstance(field, InstrumentedAttribute):
                        label = field.label
                _len = getattr(field.properties.data_type, 'length', 0)
                _prec = getattr(field.properties.data_type, 'precision', 0)
                _scale = getattr(field.properties.data_type, 'scale', 0)
                _len = _len if _len is not None else 0
                _prec = _prec if _prec is not None else 0
                _scale = _scale if _scale is not None else 0

                ret.append(
                    (
                        field.properties.name,
                        label,
                        field.properties.ftype,
                        field.properties.data_type.get_ecf_type(fakeapi),
                        _len,
                        _prec,
                        _scale,
                        field.properties.primaryKey,
                        field.properties.required,
                        field.properties.enabled,
                        field.properties.visible,
                        field.properties.readOnly,
                        tuple(tpchoice),
                        field.properties.synchronized,
                        field.properties.browseable,
                        field.properties.charcase,
                        field.properties.updateable,
                        field.properties.savestate
                    ))
        finally:
            ecfentity.session_close_all()
        return ret

    def __initexec__(self, session, extfunc):
        return self.init_program_exec(session, extfunc)

    async def __execmethod__(self, method_name, session, *args):
        exec_method = method_name
        if hasattr(self, exec_method):
            func = getattr(self, exec_method)
            if asyncio.iscoroutinefunction(func):
                return await func(session, *args)
            else:
                return func(session, *args)
        else:
            raise Exception('Method %s could not be found.' % methodname)

    async def __getsession__(self, *args, mode: int = 0, **kwargs):
        session = MVCSession(self)
        session.adapt_request(self._request)
        return await self.after_get_session(session, session.user_name) if mode == 1 else session

    async def execute_func(self, func_name: str, *args, **kwargs):
        func = getattr(self, func_name)
        return await ecfentity.safe_execute(func, *args, **kwargs)


class MVCController(MVCBaseController):

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        descriptor = cls.descriptor
        descriptor.describe(cls.__name__)
        field_counter: int = 0
        for field_name, field in cls.__dict__.items():
            if isinstance(field, MVCField):
                if field.properties.name is None:
                    field.properties.name = field_name
                field.properties.fieldNo = field_counter
                descriptor.fields.append(field_name)
                field_counter += 1
