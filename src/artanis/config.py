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
# This module is part of Centric PLM Integration Bridge and is released under
# the Apache-2.0 License: https://www.apache.org/licenses/LICENSE-2.0

# !/usr/bin/env python
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
# This module is part of Centric PLM Integration Bridge and is released under
# the Apache-2.0 License: https://www.apache.org/licenses/LICENSE-2.0
from __future__ import annotations

import os
import io
import re
import pathlib
import logging
from collections import OrderedDict
from contextlib import contextmanager
from abc import ABCMeta, abstractmethod
from typing import (IO, Dict, Iterable, Iterator, Mapping, Optional, Tuple,
                    Union, Match, NamedTuple, Pattern, Sequence, Any)

from .abc.listenable import Listenable
from .abc.singleton import SingletonObject
from .abc.objlock import SyncLock
from .exceptions import ConfigError

StrPath = Union[str, 'os.PathLike[str]']

logger = logging.getLogger(__name__)


def make_regex(string: str, extra_flags: int = 0) -> Pattern[str]:
    return re.compile(string, re.UNICODE | extra_flags)


_newline = make_regex(r"(\r\n|\n|\r)")
_multiline_whitespace = make_regex(r"\s*", extra_flags=re.MULTILINE)
_whitespace = make_regex(r"[^\S\r\n]*")
_export = make_regex(r"(?:export[^\S\r\n]+)?")
_single_quoted_key = make_regex(r"'([^']+)'")
_unquoted_key = make_regex(r"([^=\#\s]+)")
_equal_sign = make_regex(r"(=[^\S\r\n]*)")
_single_quoted_value = make_regex(r"'((?:\\'|[^'])*)'")
_double_quoted_value = make_regex(r'"((?:\\"|[^"])*)"')
_unquoted_value = make_regex(r"([^\r\n]*)")
_comment = make_regex(r"(?:[^\S\r\n]*#[^\r\n]*)?")
_end_of_line = make_regex(r"[^\S\r\n]*(?:\r\n|\n|\r|$)")
_rest_of_line = make_regex(r"[^\r\n]*(?:\r|\n|\r\n)?")
_double_quote_escapes = make_regex(r"\\[\\'\"abfnrtv]")
_single_quote_escapes = make_regex(r"\\[\\']")
_posix_variable: Pattern[str] = re.compile(
    r"""
    \$\{
        (?P<name>[^\}:]*)
        (?::-
            (?P<default>[^\}]*)
        )?
    \}
    """,
    re.VERBOSE,
)


class Configuration(SingletonObject, SyncLock, Listenable):

    ARTANIS_AUTH_ENABLED: str = 'artanis.auth.enabled'
    ARTANIS_AUTH_BINDTYPE: str = 'artanis.auth.bindtype'
    ARTANIS_AUTH_BIND: str = 'artanis.auth.bind'
    ARTANIS_AUTH_INSTANCES: str ='artanis.auth.instances'

    ARTANIS_API_ENABLED: str = 'artanis.api.enabled'
    ARTANIS_API_BINDTYPE: str = 'artanis.api.bindtype'
    ARTANIS_API_BIND: str = 'artanis.api.bind'
    ARTANIS_API_INSTANCES: str ='artanis.api.instances'

    ARTANIS_MVC_ENABLED: str = 'artanis.mvc.enabled'
    ARTANIS_MVC_BINDTYPE: str = 'artanis.mvc.bindtype'
    ARTANIS_MVC_BIND: str = 'artanis.mvc.bind'
    ARTANIS_MVC_INSTANCES: str = 'artanis.mvc.instances'

    ARTANIS_WS_ENABLED: str = 'artanis.ws.enabled'
    ARTANIS_WS_BINDTYPE: str = 'artanis.ws.bindtype'
    ARTANIS_WS_BIND: str = 'artanis.ws.bind'
    ARTANIS_WS_INSTANCES: str = 'artanis.ws.instances'

    ARTANIS_TASK_ENABLED: str = 'artanis.task.enabled'
    ARTANIS_TASK_INSTANCES: str= 'artanis.task.instances'
    ARTANIS_TASK_MAXTASK: str = 'artanis.task.maxtask'
    ARTANIS_TASK_MONITOR: str = 'artanis.task.monitor'

    ARTANIS_STATIC_ENABLED: str = 'artanis.static.enabled'
    ARTANIS_REDIS_URL: str = 'artanis.redis.url'
    ARTANIS_LOG_FILENAME: str = 'artanis.log.filename'
    ARTANIS_LOG_LEVEL: str = 'artanis.log.level'
    ARTANIS_ENV_PATH: str = 'artanis.env.path'
    ARTANIS_TMP_PATH: str = 'artanis.tmp.path'



    def __init__(self, path: Optional[StrPath]=None):
        super().__init__()
        self._config_path: Optional[StrPath] = path
        self._dict: Optional[Dict[str, Optional[str]]] = None
        self._default: Optional[Dict[str, Optional[str]]] = None

    @property
    def config_path(self):
        return self._config_path

    @config_path.setter
    def config_path(self, value):
        self._config_path = value
        self._default = OrderedDict(self.configure_default())

    def configure_default(self) -> Mapping[str, Optional[str]]:
        path = str(pathlib.Path(os.path.abspath(self.config_path))
                .parent.parent.resolve())
        values: Dict[str, Optional[str]] = {

            self.ARTANIS_AUTH_ENABLED: 'true',
            self.ARTANIS_AUTH_INSTANCES: '1',
            self.ARTANIS_AUTH_BINDTYPE: 'tcp',
            self.ARTANIS_AUTH_BIND: '0.0.0.0:8001',

            self.ARTANIS_API_ENABLED: 'false',
            self.ARTANIS_API_INSTANCES: '2',
            self.ARTANIS_API_BINDTYPE: 'tcp',
            self.ARTANIS_API_BIND: '0.0.0.0:8002',

            self.ARTANIS_MVC_ENABLED: 'false',
            self.ARTANIS_MVC_INSTANCES: '2',
            self.ARTANIS_MVC_BINDTYPE: 'tcp',
            self.ARTANIS_MVC_BIND: '0.0.0.0:8003',

            self.ARTANIS_WS_ENABLED: 'false',
            self.ARTANIS_WS_INSTANCES: '1',
            self.ARTANIS_WS_BINDTYPE: 'tcp',
            self.ARTANIS_WS_BIND: '0.0.0.0:8003',

            self.ARTANIS_TASK_ENABLED: 'true',
            self.ARTANIS_TASK_INSTANCES: '1',
            self.ARTANIS_TASK_MAXTASK: '32',
            self.ARTANIS_TASK_MONITOR: 'true',

            self.ARTANIS_STATIC_ENABLED: 'false',

            self.ARTANIS_REDIS_URL: 'redis://127.0.0.1:6379',
            self.ARTANIS_LOG_LEVEL: 'INFO',

            self.ARTANIS_ENV_PATH : path,
            self.ARTANIS_TMP_PATH : '{}/tmp'.format(path),
            self.ARTANIS_LOG_FILENAME : '{}/log/artanis.log'.format(path)
        }
        return values

    @contextmanager
    def _get_stream(self) -> Iterator[IO[str]]:
        if self.config_path and os.path.isfile(self.config_path):
            with open(self.config_path) as stream:
                yield stream
        else:
            logger.info("Could not find configuration file %s.", self.config_path, )
            yield io.StringIO('')

    def dict(self) -> Dict[str, Optional[str]]:
        """Return dotenv as dict"""
        if self._dict:
            return self._dict
        _dict:Mapping[str, Optional[str]] = self.configure_default()
        raw_values = self.parse()
        self._dict = OrderedDict(_dict)
        self._dict.update(resolve_variables(raw_values, override=True))
        return self._dict

    def parse(self) -> Iterator[Tuple[str, Optional[str]]]:
        with self._get_stream() as stream:
            for mapping in with_warn_for_invalid_lines(parse_stream(stream)):
                if mapping.key is not None:
                    yield mapping.key, mapping.value

    def get_property_value(self, key: str, default: Any = None):
        dictionary = self.dict()
        return default if key not in dictionary else dictionary[key]

    @classmethod
    def _configure_instance(cls, config_path: Optional[StrPath] = None):
        cls.VM_DEFAULT.config_path = config_path


class Original(NamedTuple):
    string: str
    line: int


class Binding(NamedTuple):
    key: Optional[str]
    value: Optional[str]
    original: Original
    error: bool


class Position:
    def __init__(self, chars: int, line: int) -> None:
        self.chars = chars
        self.line = line

    @classmethod
    def start(cls) -> "Position":
        return cls(chars=0, line=1)

    def set(self, other: "Position") -> None:
        self.chars = other.chars
        self.line = other.line

    def advance(self, string: str) -> None:
        self.chars += len(string)
        self.line += len(re.findall(_newline, string))


class Reader:
    def __init__(self, stream: IO[str]) -> None:
        self.string = stream.read()
        self.position = Position.start()
        self.mark = Position.start()

    def has_next(self) -> bool:
        return self.position.chars < len(self.string)

    def set_mark(self) -> None:
        self.mark.set(self.position)

    def get_marked(self) -> Original:
        return Original(
            string=self.string[self.mark.chars:self.position.chars],
            line=self.mark.line,
        )

    def peek(self, count: int) -> str:
        return self.string[self.position.chars:self.position.chars + count]

    def read(self, count: int) -> str:
        result = self.string[self.position.chars:self.position.chars + count]
        if len(result) < count:
            raise ConfigError("read: End of string")
        self.position.advance(result)
        return result

    def read_regex(self, regex: Pattern[str]) -> Sequence[str]:
        match = regex.match(self.string, self.position.chars)
        if match is None:
            raise ConfigError("read_regex: Pattern not found")
        self.position.advance(self.string[match.start():match.end()])
        return match.groups()


def decode_escapes(regex: Pattern[str], string: str) -> str:
    def decode_match(match: Match[str]) -> str:
        return codecs.decode(match.group(0), 'unicode-escape')  # type: ignore

    return regex.sub(decode_match, string)


def parse_key(reader: Reader) -> Optional[str]:
    char = reader.peek(1)
    if char == "#":
        return None
    elif char == "'":
        (key,) = reader.read_regex(_single_quoted_key)
    else:
        (key,) = reader.read_regex(_unquoted_key)
    return key


def parse_unquoted_value(reader: Reader) -> str:
    (part,) = reader.read_regex(_unquoted_value)
    return re.sub(r"\s+#.*", "", part).rstrip()


def parse_value(reader: Reader) -> str:
    char = reader.peek(1)
    if char == u"'":
        (value,) = reader.read_regex(_single_quoted_value)
        return decode_escapes(_single_quote_escapes, value)
    elif char == u'"':
        (value,) = reader.read_regex(_double_quoted_value)
        return decode_escapes(_double_quote_escapes, value)
    elif char in (u"", u"\n", u"\r"):
        return u""
    else:
        return parse_unquoted_value(reader)


def parse_binding(reader: Reader) -> Binding:
    reader.set_mark()
    try:
        reader.read_regex(_multiline_whitespace)
        if not reader.has_next():
            return Binding(
                key=None,
                value=None,
                original=reader.get_marked(),
                error=False,
            )
        reader.read_regex(_export)
        key = parse_key(reader)
        reader.read_regex(_whitespace)
        if reader.peek(1) == "=":
            reader.read_regex(_equal_sign)
            value: Optional[str] = parse_value(reader)
        else:
            value = None
        reader.read_regex(_comment)
        reader.read_regex(_end_of_line)
        return Binding(
            key=key,
            value=value,
            original=reader.get_marked(),
            error=False,
        )
    except ConfigError:
        reader.read_regex(_rest_of_line)
        return Binding(
            key=None,
            value=None,
            original=reader.get_marked(),
            error=True,
        )


def parse_stream(stream: IO[str]) -> Iterator[Binding]:
    reader = Reader(stream)
    while reader.has_next():
        yield parse_binding(reader)


def with_warn_for_invalid_lines(mappings: Iterator[Binding]) -> Iterator[Binding]:
    for mapping in mappings:
        if mapping.error:
            logger.warning(
                "Could not parse configuration statement starting at line %s",
                mapping.original.line,
            )
        yield mapping


class Atom(metaclass=ABCMeta):
    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    @abstractmethod
    def resolve(self, env: Mapping[str, Optional[str]]) -> str: ...


class Literal(Atom):
    def __init__(self, value: str) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"Literal(value={self.value})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash((self.__class__, self.value))

    def resolve(self, env: Mapping[str, Optional[str]]) -> str:
        return self.value


class Variable(Atom):
    def __init__(self, name: str, default: Optional[str]) -> None:
        self.name = name
        self.default = default

    def __repr__(self) -> str:
        return f"Variable(name={self.name}, default={self.default})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (self.name, self.default) == (other.name, other.default)

    def __hash__(self) -> int:
        return hash((self.__class__, self.name, self.default))

    def resolve(self, env: Mapping[str, Optional[str]]) -> str:
        default = self.default if self.default is not None else ""
        result = env.get(self.name, default)
        return result if result is not None else ""


def parse_variables(value: str) -> Iterator[Atom]:
    cursor = 0

    for match in _posix_variable.finditer(value):
        (start, end) = match.span()
        name = match["name"]
        default = match["default"]

        if start > cursor:
            yield Literal(value=value[cursor:start])

        yield Variable(name=name, default=default)
        cursor = end

    length = len(value)
    if cursor < length:
        yield Literal(value=value[cursor:length])


def resolve_variables(
        values: Iterable[Tuple[str, Optional[str]]],
        override: bool,
) -> Mapping[str, Optional[str]]:
    new_values: Dict[str, Optional[str]] = {}

    for (name, value) in values:
        if value is None:
            result = None
        else:
            atoms = parse_variables(value)
            env: Dict[str, Optional[str]] = {}
            if override:
                env.update(os.environ)  # type: ignore
                env.update(new_values)
            else:
                env.update(new_values)
                env.update(os.environ)  # type: ignore
            result = "".join(atom.resolve(env) for atom in atoms)

        new_values[name] = result

    return new_values
