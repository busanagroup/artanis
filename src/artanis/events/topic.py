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

import abc
import dataclasses
import decimal
import enum
import re
import typing as t
import uuid

T = t.TypeVar("T", bound=int | str | float | decimal.Decimal | uuid.UUID)
FragmentType = t.Literal["constant", "rest", "str", "int", "float", "decimal", "uuid"]


class Serializer(t.Generic[T], metaclass=abc.ABCMeta):
    regex: t.ClassVar[re.Pattern]
    type: t.ClassVar[type]

    @abc.abstractmethod
    def load(self, value: str) -> T: ...

    @abc.abstractmethod
    def dump(self, value: T) -> str: ...

    def __eq__(self, other):
        return type(other) == type(self)


class StringSerializer(Serializer[str]):
    regex = re.compile(r"[^.]+")
    type = str

    def load(self, value: str) -> str:
        return str(value)

    def dump(self, value: str) -> str:
        return str(value)


class IntegerSerializer(Serializer[int]):
    regex = re.compile(r"-?[0-9]+")
    type = int

    def load(self, value: str) -> int:
        return int(value)

    def dump(self, value: int) -> str:
        return str(value)


class FloatSerializer(Serializer[float]):
    regex = re.compile(r"-?[0-9]+(.[0-9]+)?")
    type = float

    def load(self, value: str) -> float:
        return float(value)

    def dump(self, value: float) -> str:
        return f"{value:0.10f}".rstrip("0").rstrip(".")


class DecimalSerializer(Serializer[decimal.Decimal]):
    regex = re.compile(r"-?[0-9]+(.[0-9]+)?")
    type = decimal.Decimal

    def load(self, value: str) -> decimal.Decimal:
        return decimal.Decimal(value)

    def dump(self, value: decimal.Decimal) -> str:
        return str(value)


class UUIDSerializer(Serializer[uuid.UUID]):
    regex = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
    type = uuid.UUID

    def load(self, value: str) -> uuid.UUID:
        return uuid.UUID(value)

    def dump(self, value: uuid.UUID) -> str:
        return str(value)


@dataclasses.dataclass
class _Fragment(abc.ABC):
    REGEX: t.ClassVar[re.Pattern] = re.compile(
        r"""
        (?P<parameter>{(?P<parameter_name>[a-zA-Z_][a-zA-Z0-9_]*)(?::(?P<parameter_type>[a-zA-Z_][a-zA-Z0-9_]*)?)?}) |
        (?P<constant>.*)
        """,
        re.X,
    )

    value: str
    type: FragmentType

    @classmethod
    def build(cls, fragment: str) -> "_Fragment":
        match = cls.REGEX.match(fragment)

        assert match

        if match.group("parameter"):
            return _FragmentParameter(
                value=fragment,
                type=t.cast(FragmentType, match.group("parameter_type") or "str"),
                name=match.group("parameter_name"),
            )
        else:
            return _FragmentConstant(value=fragment, type="constant")

    @property
    @abc.abstractmethod
    def regex(self) -> re.Pattern:
        ...

    @property
    @abc.abstractmethod
    def template(self) -> str:
        ...


@dataclasses.dataclass
class _FragmentConstant(_Fragment):
    @property
    def regex(self) -> re.Pattern:
        return re.compile(self.value)

    @property
    def template(self) -> str:
        return self.value


@dataclasses.dataclass
class _FragmentParameter(_Fragment):
    SERIALIZERS: t.ClassVar[dict[FragmentType, Serializer]] = {
        "str": StringSerializer(),
        "int": IntegerSerializer(),
        "float": FloatSerializer(),
        "decimal": DecimalSerializer(),
        "uuid": UUIDSerializer(),
    }

    name: str = dataclasses.field(repr=False, hash=False, compare=False)
    serializer: Serializer = dataclasses.field(init=False, repr=False, hash=False, compare=False)

    def __post_init__(self):
        try:
            self.serializer = self.SERIALIZERS[self.type]
        except KeyError:
            raise ValueError(f"Unknown topic serializer '{self.type}'")

    @property
    def regex(self) -> re.Pattern:
        return re.compile(rf"(?P<{self.name}>{self.serializer.regex.pattern})")

    @property
    def template(self) -> str:
        return f"{{{self.name}}}"


class _Match(enum.Enum):
    exact = enum.auto()
    partial = enum.auto()
    none = enum.auto()


@dataclasses.dataclass
class _MatchResult:
    match: _Match
    parameters: dict[str, t.Any] | None
    matched: str | None
    unmatched: str | None


@dataclasses.dataclass
class _BuildResult:
    topic: str
    unused: dict[str, t.Any]

def topic_as_path(topic: str) -> str:
    path = topic.replace(".", "/")
    return "/" + path if not path.startswith("/") else path


class Topic:
    Match = _Match

    def __init__(self, topic: "str | Topic"):
        """Topic with a regex to allow NS params as placeholders.

        Given a topic string like: "foo.{bar:str}"
        topic:        "foo.{bar:str}"
        template:    "foo.{bar}"
        regex:       "^foo.(?P<bar>[^.]+)$"

        :param topic: topic name space.
        """
        if isinstance(topic, Topic):
            self.topic = topic.topic
            self.path = topic.path
            self._fragments = topic._fragments
            self._parameters = topic._parameters
            self._regex = topic._regex
            self._template = topic._template
        else:
            if topic == "" or topic is None:
                raise ValueError("Invalid topic specified")
            self.topic = topic
            self.path = "/" if topic == "*" else  topic_as_path(topic)
            self._fragments = [_Fragment.build(x) for x in self.path.strip("/").split("/")]
            self._parameters: dict[str, _FragmentParameter] = {
                f.name: f for f in self._fragments if isinstance(f, _FragmentParameter)
            }

            starting_slash = "/" if self.path != "" else ""
            trailing_slash = "/" if self.path != "/" and self.path.endswith("/") else ""

            fragments_templates = "/".join(f.template for f in self._fragments)
            self._template = f"{starting_slash}{fragments_templates}{trailing_slash}"
            fragments_regex = "/".join(f.regex.pattern for f in self._fragments)
            self._regex = re.compile(
                rf"^(?P<__matched__>{starting_slash}{fragments_regex}{trailing_slash})(?P<__unmatched__>.*)$"
            )

    @property
    def parameters(self) -> dict[str, type]:
        return {f.name: f.serializer.type for f in self._parameters.values()}

    def match(self, topic: "str | Topic") -> _MatchResult:
        """Check if given topic matches with current object.

        :param topic: Topic to match
        :return: Matching result, parameters serialized values and matching parts of the topic.
        """
        if (match := self._regex.match(str(topic))) is None:
            return _MatchResult(self.Match.none, None, None, None)

        return _MatchResult(
            match=self.Match.partial if match.group("__unmatched__") else self.Match.exact,
            parameters={
                k: self._parameters[k].serializer.load(v)
                for k, v in match.groupdict().items()
                if k not in ("__matched__", "__unmatched__")
            },
            matched=match.group("__matched__") or None,
            unmatched=match.group("__unmatched__") or None,
        )

    def build(self, **params: t.Any) -> _BuildResult:
        """Build a topic by completing param placeholders with given values.

        :param params: Param values.
        :return: Built topic and unused params.
        """
        if not set(self._parameters.keys()) <= set(params.keys()):
            formatted_params = ", ".join(f"'{x}'" for x in self._parameters.keys())
            raise ValueError(f"Wrong params, expected: {formatted_params}.")

        return _BuildResult(
            topic=self._template.format(
                **{k: self._parameters[k].serializer.dump(v) for k, v in params.items() if k in self._parameters}
            ),
            unused={k: v for k, v in params.items() if k not in self._parameters},
        )

    def __bool__(self) -> bool:
        return self.topic != ""

    def __hash__(self) -> int:
        return hash(self.topic)

    def __eq__(self, other, /) -> bool:
        return isinstance(other, Topic) and self.topic.__eq__(other.topic) or self.topic.__eq__(other)

    def __str__(self) -> str:
        return self._template.__str__()

    def __repr__(self) -> str:
        return self.topic.__repr__()

    def __truediv__(self, other: "str | Topic") -> "Topic":
        if isinstance(other, Topic):
            a, b = self.topic.rstrip("."), other.topic.lstrip(".")
        elif isinstance(other, str):
            a, b = self.topic.rstrip("."), other.lstrip(".")
        else:
            raise TypeError(f"Can only concatenate str or {self.__class__.__name__} to {self.__class__.__name__}")

        return Topic(f"{a}.{b}")

    def __rtruediv__(self, other: "str | Topic") -> "Topic":
        if isinstance(other, Topic):
            a, b = other.topic.rstrip("."), self.topic.lstrip(".")  # pragma: no cover # covered by __truediv__
        elif isinstance(other, str):
            a, b = other.rstrip("."), self.topic.lstrip(".")
        else:
            raise TypeError(f"Can only concatenate str or {self.__class__.__name__} to {self.__class__.__name__}")

        return Topic(f"{a}.{b}")

    def __itruediv__(self, other: "str | Topic") -> "Topic":
        topic = self / other
        self.topic = topic.topic
        self._fragments = topic._fragments
        self._parameters = topic._parameters
        self._regex = topic._regex
        self._template = topic._template

        return self
