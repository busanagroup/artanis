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

import re
from typing import NamedTuple, Optional, Union, Dict, Any
from urllib.parse import quote, unquote

from artanis import exceptions


class URL(NamedTuple):
    """A simple representation of a URL."""

    username: Optional[str]
    """username string"""

    password: Optional[str]
    """password, which is normally a string but may also be any
    object that has a ``__str__()`` method."""

    host: Optional[str]
    """hostname or IP number.  May also be a data source name for some
    drivers."""

    port: Optional[int]
    """integer port number"""

    database: Optional[str]
    """database name"""

    @classmethod
    def create(
            cls,
            username: Optional[str] = None,
            password: Optional[str] = None,
            host: Optional[str] = None,
            port: Optional[int] = None,
            database: Optional[str] = None,
    ) -> URL:
        return cls(
            cls._assert_none_str(username, "username"),
            password,
            cls._assert_none_str(host, "host"),
            cls._assert_port(port),
            cls._assert_none_str(database, "database"),
        )

    @classmethod
    def _assert_port(cls, port: Optional[int]) -> Optional[int]:
        if port is None:
            return None
        try:
            return int(port)
        except TypeError:
            raise TypeError("Port argument must be an integer or None")

    @classmethod
    def _assert_str(cls, v: str, paramname: str) -> str:
        if not isinstance(v, str):
            raise TypeError("%s must be a string" % paramname)
        return v

    @classmethod
    def _assert_none_str(
            cls, v: Optional[str], paramname: str
    ) -> Optional[str]:
        if v is None:
            return v

        return cls._assert_str(v, paramname)

    def set(
            self,
            username: Optional[str] = None,
            password: Optional[str] = None,
            host: Optional[str] = None,
            port: Optional[int] = None,
            database: Optional[str] = None,
    ) -> URL:
        kw: Dict[str, Any] = {}
        if username is not None:
            kw["username"] = username
        if password is not None:
            kw["password"] = password
        if host is not None:
            kw["host"] = host
        if port is not None:
            kw["port"] = port
        if database is not None:
            kw["database"] = database
        return self._assert_replace(**kw)

    def _assert_replace(self, **kw: Any) -> URL:
        """argument checks before calling _replace()"""

        for name in "username", "host", "database":
            if name in kw:
                self._assert_none_str(kw[name], name)
        if "port" in kw:
            self._assert_port(kw["port"])
        return self._replace(**kw)

    def __repr__(self) -> str:
        return self.render_as_string()

    def render_as_string(self, hide_password: bool = True) -> str:
        s = ""
        if self.username is not None:
            s += quote(self.username, safe=" +")
            if self.password is not None:
                s += ":" + (
                    "***"
                    if hide_password
                    else quote(str(self.password), safe=" +")
                )
            s += "@"
        if self.host is not None:
            if ":" in self.host:
                s += f"[{self.host}]"
            else:
                s += self.host
        if self.port is not None:
            s += ":" + str(self.port)
        if self.database is not None:
            s += "/" + self.database
        return s

    def __repr__(self) -> str:
        return self.render_as_string()

    def __copy__(self) -> URL:
        return self.__class__.create(
            self.username,
            self.password,
            self.host,
            self.port,
            self.database,
        )

    def __deepcopy__(self, memo: Any) -> URL:
        return self.__copy__()

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: Any) -> bool:
        return (
                isinstance(other, URL)
                and self.username == other.username
                and self.password == other.password
                and self.host == other.host
                and self.database == other.database
                and self.port == other.port
        )

    def __ne__(self, other: Any) -> bool:
        return not self == other


def make_url(name_or_url: Union[str, URL]) -> URL:
    if isinstance(name_or_url, str):
        return _parse_url(name_or_url)
    elif not isinstance(name_or_url, URL) and not hasattr(
            name_or_url, "_sqla_is_testing_if_this_is_a_mock_object"
    ):
        raise exceptions.ArgumentError(
            f"Expected string or URL object, got {name_or_url!r}"
        )
    else:
        return name_or_url


def _parse_url(name: str) -> URL:
    pattern = re.compile(
        r"""
            (?:
                (?P<username>[^:/]*)
                (?::(?P<password>[^@]*))?
            @)?
            (?:
                (?:
                    \[(?P<ipv6host>[^/\?]+)\] |
                    (?P<ipv4host>[^/:\?]+)
                )?
                (?::(?P<port>[^/\?]*))?
            )?
            (?:/(?P<database>[^\?]*))?
            """,
        re.X,
    )

    m = pattern.match(name)
    if m is not None:
        components = m.groupdict()
        if components["username"] is not None:
            components["username"] = unquote(components["username"])
        if components["password"] is not None:
            components["password"] = unquote(components["password"])
        ipv4host = components.pop("ipv4host")
        ipv6host = components.pop("ipv6host")
        components["host"] = ipv4host or ipv6host
        if components["port"]:
            components["port"] = int(components["port"])
        return URL.create(**components)  # type: ignore

    else:
        raise exceptions.ArgumentError(
            "Could not parse URL from given URL string"
        )
