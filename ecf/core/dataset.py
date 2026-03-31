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
import decimal as dcm

import copy
import enum
import typing
from collections import OrderedDict

from ecf.core.dateutils import *


@enum.unique
class DatasetState(enum.Enum):
    DS_INACTIVE = 0
    DS_BROWSE = 1
    DS_APPEND = 2
    DS_EDIT = 3
    DS_DELETE = 4


class FieldType:
    FT_NAMES = ["UNKNOWN", "STRING", "SMALLINT", "INTEGER", "WORD", "BOOLEAN", "FLOAT", "CURRENCY", "BCD", "DATE",
                "TIME", "DATETIME", "BYTES", "VARBYTES", "AUTOINC", "BLOB", "MEMO", "GRAPHIC", "FMTMEMO", "PARADOXOLE",
                "DBASEOLE", "TYPEDBINARY", "CURSOR", "FIXEDCHAR", "WIDESTRING", "LARGEINT", "ADT", "ARRAY", "REFERENCE",
                "DATASET", "HUGEBLOB", "HUGECLOB", "VARIANT", "INTERFACE", "DISPATCH", "GUID", "SQLTIMESTAMP",
                "FMTBCDFIELD", "FIXEDWIDECHAR", "WIDEMEMO", "LONGWORD", "SHORTINT", "BYTE",
                "EXTENDED", "CONNECTION", "PARAMS", "STREAM", "SQLTIMESTAMPOFFSET", "OBJECT", "SINGLE"]

    @classmethod
    def get_field_type_name(cls, datatype: DataType) -> str:
        return cls.FT_NAMES[datatype] if datatype < len(cls.FT_NAMES) else None

    @classmethod
    def get_field_type(cls, typename: str) -> DataType | None:
        _typename = typename.upper()
        return cls.FT_NAMES.index(_typename) if _typename in cls.FT_NAMES else None


@enum.unique
class DataType(enum.IntEnum):
    FT_UNKNOWN = 0
    FT_STRING = 1
    FT_SMALLINT = 2
    FT_INTEGER = 3
    FT_WORD = 4
    FT_BOOLEAN = 5
    FT_FLOAT = 6
    FT_CURRENCY = 7
    FT_BCD = 8
    FT_DATE = 9
    FT_TIME = 10
    FT_DATETIME = 11
    FT_BYTES = 12
    FT_VARBYTES = 13
    FT_AUTOINC = 14
    FT_BLOB = 15
    FT_MEMO = 16
    FT_GRAPHIC = 17
    FT_FMTMEMO = 18
    FT_PARADOXOLE = 19
    FT_DBASEOLE = 20
    FT_TYPEDBINARY = 21
    FT_CURSOR = 22
    FT_FIXEDCHAR = 23
    FT_WIDESTRING = 24
    FT_LARGEINT = 25
    FT_ADT = 26
    FT_ARRAY = 27
    FT_REFERENCE = 28
    FT_DATASET = 29
    FT_HUGEBLOB = 30
    FT_HUGECLOB = 31
    FT_VARIANT = 32
    FT_INTERFACE = 33
    FT_DISPATCH = 34
    FT_GUID = 35
    FT_SQLTIMESTAMP = 36
    FT_FMTBCDFIELD = 37
    FT_FIXEDWIDECHAR = 38
    FT_WIDEMEMO = 39
    FT_LONGWORD = 40
    FT_SHORTINT = 41
    FT_BYTE = 42
    FT_EXTENDED = 43
    FT_CONNECTION = 44
    FT_PARAMS = 45
    FT_STREAM = 46
    FT_SQLTIMESTAMPOFFSET = 47
    FT_OBJECT = 48
    FT_SINGLE = 49


class VirtualDatasetException(Exception):
    ...


class VirtualDataset(object):
    field_info: OrderedDict
    field_sequence: list = []
    rowset: list = []
    active_recordset: list = []
    record_position: int = 0
    dataset_state: DatasetState = DatasetState.DS_INACTIVE

    def set_field_value(self, field_name: str, value: typing.Any):
        if self.state == DatasetState.DS_INACTIVE:
            raise VirtualDatasetException("Dataset state is not in opened")
        elif self.state not in [DatasetState.DS_APPEND, DatasetState.DS_EDIT, DatasetState.DS_DELETE]:
            raise VirtualDatasetException("Dataset state is not in valid state")
        field_index = self.field_sequence.index(field_name)
        if field_index > -1:
            self.active_recordset[field_index] = self.encode_value_type(value, self.field_info[field_name])

    def get_field_value(self, field_name: str) -> typing.Any:
        if self.state == DatasetState.DS_INACTIVE:
            raise VirtualDatasetException("Dataset state is not in opened")
        field_index = self.field_sequence.index(field_name)
        return None if field_index <= -1 \
            else self.decode_value_type(self.active_recordset[field_index], self.field_info[field_name])

    def get_fields_as_dict(self, field_names: list) -> dict:
        if self.state == DatasetState.DS_INACTIVE:
            raise VirtualDatasetException("Dataset state is not in opened")
        return dict([(field_name, self.decode_value_type(self.active_recordset[self.field_sequence.index(field_name)],
                                                         self.field_info[field_name]))
                     for field_name in field_names])

    def get_empty_fields(self):
        return dict([(field_name, None) for field_name in self.field_info.keys()])

    def get_field_oldvalue(self, field_name: str) -> typing.Any:
        field_index = self.field_sequence.index(field_name)
        old_recordset = self.rowset[self.record_position]
        return None if field_index <= -1 \
            else self.decode_value_type(old_recordset[field_index], self.field_info[field_name])

    def decode_value_type(self, value: typing.Any, field_info: list):
        data_type = FieldType.get_field_type(field_info[4])
        result = None
        match data_type:
            case DataType.FT_DATE:
                result = delphi_to_datelong(value)
            case DataType.FT_TIME:
                result = delphi_to_timelong(value)
            case DataType.FT_DATETIME:
                result = delphi_to_datetimelong(value)
            case _:
                result = value
        return result

    def encode_value_type(self, value: typing.Any, field_info: list):
        data_type = FieldType.get_field_type(field_info[4])
        result = None
        match data_type:
            case DataType.FT_DATE:
                if isinstance(value, int):
                    result = delphi_from_datelong(value)
                elif isinstance(value, float):
                    result = delphi_from_datelong(int(value))
                elif isinstance(value, dt.date):
                    result = delphi_from_date(value)
                elif isinstance(value, dt.datetime):
                    result = delphi_from_datetime(value)
                elif isinstance(value, dt.time):
                    result = 0
                elif isinstance(value, dcm.Decimal) or isinstance(value, str):
                    list_d = str(value).split(".")
                    result = delphi_from_datelong(int(list_d[0]))
            case DataType.FT_TIME:
                if isinstance(value, int):
                    result = delphi_from_timelong(value)
                elif isinstance(value, float):
                    result = delphi_from_timelong(int(value))
                elif isinstance(value, dt.date):
                    result = 0
                elif isinstance(value, dt.datetime):
                    result = delphi_from_datetime(value)
                elif isinstance(value, dt.time):
                    result = float(0) + delphi_from_time(value)
                elif isinstance(value, dcm.Decimal) or isinstance(value, str):
                    list_d = str(value).split(".")
                    result = delphi_from_timelong(int(list_d[0]))
            case DataType.FT_DATETIME:
                if isinstance(value, int):
                    result = delphi_from_datetimelong(value)
                elif isinstance(value, float):
                    result = delphi_from_datetimelong(int(value))
                elif isinstance(value, dt.date):
                    result = delphi_from_date(value)
                elif isinstance(value, dt.datetime):
                    result = delphi_from_datetime(value)
                elif isinstance(value, dt.time):
                    result = float(0) + delphi_from_time(value)
                elif isinstance(value, dcm.Decimal) or isinstance(value, str):
                    list_d = str(value).split(".")
                    result = delphi_from_datetimelong(int(list_d[0]))
            case _:
                result = value
        return result

    def bind_dataset(self, field_info: list, kind: int):
        self.clear()
        fields = [(info[1], info) for info in field_info if info[3] & kind == kind]
        self.field_info.update(fields)
        self.field_sequence.extend([item[0] for item in fields])

    def from_array(self, values: list):
        if not isinstance(values, list):
            return
        self.empty_dataset()
        self.rowset = copy.deepcopy(values[1])
        if not self.active:
            self.open()
        else:
            self.do_refresh()

    def to_array(self):
        result = [copy.deepcopy(self.field_sequence), copy.deepcopy(self.rowset)]
        self.empty_dataset()
        return result

    def clear(self):
        self.rowset.clear()
        self.field_info.clear()
        self.field_sequence.clear()
        self.active_recordset.clear()
        self.record_position = 0
        self.dataset_state = DatasetState.DS_INACTIVE

    @property
    def active(self) -> bool:
        return self.dataset_state > DatasetState.DS_INACTIVE

    def open(self):
        if self.active:
            return
        self.do_refresh()
        self.dataset_state = DatasetState.DS_BROWSE

    @property
    def state(self) -> DatasetState:
        return self.dataset_state

    @property
    def record_count(self) -> int:
        return len(self.rowset)

    def do_refresh(self):
        self.record_position = 0
        if self.record_count > 0:
            temp = self.rowset[self.record_position]
            self.active_recordset = copy.deepcopy(temp)
        else:
            self.clear_recordset()

    def clear_recordset(self):
        self.active_recordset = [None] * len(self.active_recordset)

    def empty_dataset(self):
        self.clear_recordset()
        self.rowset.clear()
        self.record_position = 0

    def next(self):
        if self.active and not self.eof:
            self.record_position += 1
            self.update_active_recordset()

    def append(self):
        if len(self.field_info) == 0:
            raise VirtualDatasetException("Dataset has not been setup properly")
        if self.dataset_state == DatasetState.DS_INACTIVE:
            raise VirtualDatasetException("Dataset is not opened")
        if self.dataset_state == DatasetState.DS_BROWSE:
            raise VirtualDatasetException("Dataset is in browse mode")
        self.clear_recordset()
        self.dataset_state = DatasetState.DS_APPEND

    def edit(self):
        if len(self.field_info) == 0:
            raise VirtualDatasetException("Dataset has not been setup properly")
        if self.dataset_state == DatasetState.DS_INACTIVE:
            raise VirtualDatasetException("Dataset is not opened")
        if self.dataset_state == DatasetState.DS_BROWSE:
            raise VirtualDatasetException("Dataset is in browse mode")
        self.clear_recordset()
        if self.record_count == 0:
            raise VirtualDatasetException("Dataset is empty, cannot edit")
        elif self.record_position < 0:
            self.record_position = 0
        elif self.record_position > self.record_count:
            self.record_position = self.record_count - 1
        self.clear_recordset()
        self.update_active_recordset()
        self.dataset_state = DatasetState.DS_EDIT

    def delete(self):
        if len(self.field_info) == 0:
            raise VirtualDatasetException("Dataset has not been setup properly")
        if self.dataset_state == DatasetState.DS_INACTIVE:
            raise VirtualDatasetException("Dataset is not opened")
        if self.dataset_state == DatasetState.DS_BROWSE:
            raise VirtualDatasetException("Dataset is in browse mode")
        self.clear_recordset()
        if self.record_count == 0:
            raise VirtualDatasetException("Dataset is empty, cannot delete")
        elif self.record_position < 0:
            self.record_position = 0
        elif self.record_position > self.record_count:
            self.record_position = self.record_count - 1
        self.clear_recordset()
        self.update_active_recordset()
        self.dataset_state = DatasetState.DS_DELETE

    def post(self):
        if len(self.field_info) == 0:
            raise VirtualDatasetException("Dataset has not been setup properly")
        if self.dataset_state == DatasetState.DS_INACTIVE:
            raise VirtualDatasetException("Dataset is not opened")
        if self.dataset_state not in [DatasetState.DS_APPEND, DatasetState.DS_EDIT]:
            raise VirtualDatasetException("Dataset is not in valid state")
        match self.dataset_state:
            case DatasetState.DS_APPEND:
                temp = copy.deepcopy(self.active_recordset)
                self.rowset.append(temp)
                self.record_position += 1
                self.dataset_state = DatasetState.DS_BROWSE
            case DatasetState.DS_EDIT:
                temp = copy.deepcopy(self.active_recordset)
                self.rowset[self.record_position] = temp
                self.dataset_state = DatasetState.DS_BROWSE
            case DatasetState.DS_DELETE:
                del self.rowset[self.record_position]
                record_count = self.record_count
                if self.record_position >= record_count:
                    self.record_position = record_count - 1
                self.update_active_recordset()
                self.dataset_state = DatasetState.DS_BROWSE

    def cancel(self):
        if len(self.field_info) == 0:
            raise VirtualDatasetException("Dataset has not been setup properly")
        if self.dataset_state == DatasetState.DS_INACTIVE:
            raise VirtualDatasetException("Dataset is not opened")
        if self.dataset_state not in [DatasetState.DS_APPEND, DatasetState.DS_EDIT]:
            raise VirtualDatasetException("Dataset is not in valid state")
        self.update_active_recordset()
        self.dataset_state = DatasetState.DS_BROWSE

    def update_active_recordset(self):
        temp = self.rowset[self.record_position]
        self.rowset[self.record_position] = temp
        self.active_recordset = copy.deepcopy(temp)

    def set_recordset_from_dict(self, dict_value: dict):
        if len(self.field_info) == 0:
            raise VirtualDatasetException("Dataset has not been setup properly")
        if self.dataset_state == DatasetState.DS_INACTIVE:
            raise VirtualDatasetException("Dataset is not opened")
        if self.dataset_state not in [DatasetState.DS_APPEND, DatasetState.DS_EDIT]:
            raise VirtualDatasetException("Dataset is not in valid state")
        for key, value in dict_value.items():
            field_index = self.field_sequence.index(key)
            if field_index > -1:
                self.active_recordset[field_index] = self.encode_value_type(value, self.field_info[key])

    @property
    def eof(self):
        return self.record_position >= (self.record_count - 1)

    @property
    def bof(self):
        return self.record_position == 0
