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


import io
import logging
import os
import pathlib
import re
import uuid
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from collections.abc import Mapping
from contextlib import contextmanager
from typing import (IO, Dict, Iterable, Iterator, Optional, Tuple,
                    Union, Match, NamedTuple, Pattern, Sequence, Any)

from starlette.datastructures import State

from .abc.listenable import Listenable
from .abc.objlock import SyncLock
from .abc.singleton import Singleton
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


class Configuration(Singleton, SyncLock, Listenable):
    ARTANIS_APP_NAME: str = 'artanis.app.name'
    ARTANIS_CMP_NAME: str = 'artanis.cmp.name'
    ARTANIS_AUTH_ENABLED: str = 'artanis.auth.enabled'
    ARTANIS_AUTH_BINDTYPE: str = 'artanis.auth.bindtype'
    ARTANIS_AUTH_BIND: str = 'artanis.auth.bind'
    ARTANIS_AUTH_INSTANCES: str = 'artanis.auth.instances'

    ARTANIS_API_ENABLED: str = 'artanis.api.enabled'
    ARTANIS_API_BINDTYPE: str = 'artanis.api.bindtype'
    ARTANIS_API_BIND: str = 'artanis.api.bind'
    ARTANIS_API_INSTANCES: str = 'artanis.api.instances'

    ARTANIS_MVC_ENABLED: str = 'artanis.mvc.enabled'
    ARTANIS_MVC_BINDTYPE: str = 'artanis.mvc.bindtype'
    ARTANIS_MVC_BIND: str = 'artanis.mvc.bind'
    ARTANIS_MVC_INSTANCES: str = 'artanis.mvc.instances'

    ARTANIS_WS_ENABLED: str = 'artanis.ws.enabled'
    ARTANIS_WS_BINDTYPE: str = 'artanis.ws.bindtype'
    ARTANIS_WS_BIND: str = 'artanis.ws.bind'
    ARTANIS_WS_INSTANCES: str = 'artanis.ws.instances'

    ARTANIS_TASK_ENABLED: str = 'artanis.task.enabled'
    ARTANIS_TASK_INSTANCES: str = 'artanis.task.instances'
    ARTANIS_TASK_MAXTASK: str = 'artanis.task.maxtask'
    ARTANIS_TASK_MONITOR: str = 'artanis.task.monitor'
    ARTANIS_SPV_ENABLED: str = 'artanis.supervisor.enabled'

    ARTANIS_STATIC_ENABLED: str = 'artanis.static.enabled'
    ARTANIS_REDIS_URL: str = 'artanis.redis.url'
    ARTANIS_LOG_PATH: str = 'artanis.log.filename'
    ARTANIS_LOG_FORMAT: str = 'artanis.log.format'
    ARTANIS_LOG_LEVEL: str = 'artanis.log.level'
    ARTANIS_ENV_PATH: str = 'artanis.env.path'
    ARTANIS_TMP_PATH: str = 'artanis.tmp.path'

    ARTANIS_DB_CONNECTION: str = 'artanis.db.connection'
    ARTANIS_DB_SCHEMA: str = 'artanis.db.schema'
    ARTANIS_DB_POOL_SIZE: str = 'artanis.db.pool.size'
    ARTANIS_DB_POOL_ACTIVE: str = 'artanis.db.pool.active'
    ARTANIS_DB_POOL_IDLE: str = 'artanis.db.pool.idle'

    ARTANIS_SECURITY_CORS_ORIGINS: str = 'artanis.security.cors.origins'

    ARTANIS_DB_EXTCONN_COUNT: str = 'artanis.db.extconn.count'

    JWT_SECRET_KEY : str = 'artanis.jwt.secret.key'
    JWT_HEADER_KEY : str = 'artanis.jwt.header.key'
    JWT_HEADER_PREFIX : str = 'artanis.jwt.header.prefix'
    JWT_ALGORITHM : str = 'artanis.jwt.algorithm'
    JWT_TOKEN_EXPIRATION : str = 'artanis.jwt.token.expiration'
    JWT_REFRESH_EXPIRATION : str = 'artanis.jwt.refresh.expiration'
    JWT_ACCESS_COOKIE_KEY : str = 'artanis.jwt.access.key'
    JWT_REFRESH_COOKIE_KEY : str = 'artanis.jwt.refresh.key'

    # ARTANIS_DB_EXTCONN_1_NAME: str = 'artanis.db.extconn.1.name'
    # ARTANIS_DB_EXTCONN_1_CONNECTION: str = 'artanis.db.extconn.1.connection'
    # ARTANIS_DB_EXTCONN_1_SCHEMA: str = 'artanis.db.extconn.1.schema'

    def __init__(self, path: Optional[StrPath] = None):
        super().__init__()
        self._config_path: Optional[StrPath] = path
        self._dict: Optional[Dict[str, Optional[str]]] = None
        self._default: Optional[Dict[str, Optional[str]]] = None
        self.container: State | None = State({})
        self._server_up: bool = False

    @property
    def server_is_ready(self):
        return self._server_up

    @server_is_ready.setter
    def server_is_ready(self, value):
        self._server_up = value

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

            self.ARTANIS_APP_NAME: 'Artanis',
            self.ARTANIS_CMP_NAME: 'Busana Apparel Group',

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
            self.ARTANIS_WS_BIND: '0.0.0.0:8004',

            self.ARTANIS_TASK_ENABLED: 'true',
            self.ARTANIS_TASK_INSTANCES: '1',
            self.ARTANIS_TASK_MAXTASK: '32',
            self.ARTANIS_TASK_MONITOR: 'true',

            self.ARTANIS_STATIC_ENABLED: 'false',
            self.ARTANIS_SPV_ENABLED: 'true',

            self.ARTANIS_REDIS_URL: 'redis://127.0.0.1:6379',

            self.ARTANIS_ENV_PATH: path,
            self.ARTANIS_TMP_PATH: '{}/tmp'.format(path),

            self.ARTANIS_LOG_LEVEL: 'INFO',
            self.ARTANIS_LOG_FORMAT: '[%(asctime)s][%(name)s][%(levelname)-7s][%(process)d] %(message)s',
            self.ARTANIS_LOG_PATH: '{}/log/artanis'.format(path),

            self.ARTANIS_DB_CONNECTION: "postgresql+asyncpg://postgres:masterkey@10.0.3.102/template1",
            self.ARTANIS_DB_SCHEMA: None,
            self.ARTANIS_DB_POOL_SIZE: None,
            self.ARTANIS_DB_POOL_ACTIVE: None,
            self.ARTANIS_DB_POOL_IDLE: None,

            self.ARTANIS_SECURITY_CORS_ORIGINS: '',

            self.JWT_SECRET_KEY : str(uuid.uuid5(uuid.NAMESPACE_OID, 'Artanis')),
            self.JWT_HEADER_KEY : "Authorization",  # Authorization header identity
            self.JWT_HEADER_PREFIX : "Bearer",  # Bearer prefix
            self.JWT_ALGORITHM : "HS256",  # Algorithm used to sign the token
            self.JWT_TOKEN_EXPIRATION : "1800",  # 30 minutes in seconds
            self.JWT_REFRESH_EXPIRATION : "7200",  # 2 hours in seconds
            self.JWT_ACCESS_COOKIE_KEY : "access_token",
            self.JWT_REFRESH_COOKIE_KEY : "refresh_token",
        }
        return values

    def configure_logging(self, subsys_name: str = None, subsys_index: int = None):
        file_name = self.get_property_value(self.ARTANIS_LOG_PATH)
        if subsys_name is not None:
            file_name += f"-{subsys_name}"
        if subsys_index is not None:
            file_name += f"-{subsys_index}"
        file_name += '.log'
        # file_handler = TimedRotatingFileHandler(file_name, when='D', backupCount=5)
        logging.basicConfig(
            level=logging.getLevelName(self.get_property_value(self.ARTANIS_LOG_LEVEL, 'INFO').upper()),
            format=self.get_property_value(self.ARTANIS_LOG_FORMAT),
            # handlers=[file_handler, ]
        )

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
        _dict: Mapping[str, Optional[str]] = self.configure_default()
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
        return default if key not in dictionary or not dictionary[key] else dictionary[key]

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
