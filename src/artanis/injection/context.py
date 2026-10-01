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
import typing as t

__all__ = ["C", "Context", "ContextType", "Field"]

from artanis.injection.exceptions import ContextError

C = t.TypeVar("C", bound="Context")
V = t.TypeVar("V")


class Field(t.Generic[V]):
    """A typed context field implemented as a data descriptor.

    The field type is declared once and drives both static typing (through the generic parameter) and runtime
    behaviour (annotation matching for dependency injection and the required-value guard). Values live in the owner
    context internal data mapping, never as plain instance attributes, so all reads, writes and deletions funnel
    through this descriptor.
    """

    name: str

    @t.overload
    def __init__(
        self: "Field[V]", type_: type[V], *, required: t.Literal[True] = True, hashable: bool = True
    ) -> None: ...
    @t.overload
    def __init__(
        self: "Field[V | None]", type_: type[V], *, required: t.Literal[False], hashable: bool = True
    ) -> None: ...
    def __init__(self, type_: type[V], *, required: bool = True, hashable: bool = True) -> None:
        """Declare a context field.

        :param type_: The non-nullable type provided by this field.
        :param required: Whether reading the field while it is missing must raise. Defaults to True.
        :param hashable: Whether the field participates in the context hash. Defaults to True.
        """
        self.type = type_
        self.required = required
        self.hashable = hashable

    def __set_name__(self, owner: "type[Context]", name: str) -> None:
        self.name = name

    @t.overload
    def __get__(self, instance: None, owner: type, /) -> "Field[V]": ...
    @t.overload
    def __get__(self, instance: "Context", owner: type | None = None, /) -> V: ...
    def __get__(self, instance: "Context | None", owner: type | None = None, /) -> t.Any:
        if instance is None:
            return self

        value = instance._data.get(self.name)
        if value is None and self.required:
            raise ContextError(f"Invalid '{self.name}' in context")

        return value

    def __set__(self, instance: "Context", value: V, /) -> None:
        instance._data[self.name] = value

    def __delete__(self, instance: "Context", /) -> None:
        instance._data.pop(self.name, None)


class ContextType(type):
    """Metaclass that builds the field registry of a context at class-creation time.

    Scanning the MRO once when the class is defined keeps ``__fields__`` and ``__types__`` as eager, introspectable
    class attributes, so the context itself needs no lazy caching.
    """

    def __new__(mcs, name: str, bases: tuple[type, ...], namespace: dict[str, t.Any], **kwargs: t.Any) -> type:
        namespace["__fields__"] = {
            **{n: v for base in bases for n, v in getattr(base, "__fields__", {}).items()},
            **{n: v for n, v in namespace.items() if isinstance(v, Field)},
        }
        namespace["__types__"] = {n: f.type for n, f in namespace["__fields__"].items()}
        return super().__new__(mcs, name, bases, namespace, **kwargs)


def _hashable(obj: t.Any) -> t.Hashable:
    if isinstance(obj, dict):
        return tuple(sorted([(k, _hashable(v)) for k, v in obj.items()]))

    if isinstance(obj, list | tuple | set | frozenset):
        return tuple([_hashable(x) for x in obj])

    return obj


class Context(t.MutableMapping[str, t.Any]):
    types: t.ClassVar[dict[str, type]]
    hashable: t.ClassVar[t.Sequence[str] | None] = None

    def __init__(self, d: t.Mapping[str, t.Any], /) -> None:
        if invalid_keys := [k for k in d.keys() if k not in self.types]:
            raise ContextError(f"Invalid keys ({','.join(invalid_keys)})")

        self._data = dict(d)

    def __getitem__(self, key: str, /) -> t.Any:
        return self._data.__getitem__(key)

    def __setitem__(self, key: str, value: t.Any, /) -> None:
        return self._data.__setitem__(key, value)

    def __delitem__(self, key: str, /) -> None:
        return self._data.__delitem__(key)

    def __iter__(self) -> t.Iterator[str]:
        return self._data.__iter__()

    def __hash__(self) -> int:
        return hash(_hashable([(k, v) for k, v in self._data.items() if not self.hashable or k in self.hashable]))

    def __eq__(self, other: object, /) -> bool:
        return self._data.__eq__(other._data if isinstance(other, Context) else other)

    def __len__(self) -> int:
        return self._data.__len__()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self._data.__str__()})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._data.__repr__()})"
