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
import datetime
import os
import pathlib
import struct
import typing as t
import uuid
import warnings

from artanis import exceptions
from artanis.asgi import types
from artanis.serialize.compression import Compression
from artanis.serialize.datastructures import Artifacts, ModelArtifact
from artanis.serialize.model_serializers import ModelSerializer
from artanis.serialize.protocols import Protocol

__all__ = ["Serializer", "dump", "load"]


class Serializer:
    """Main class for serializing and deserializing ML models in Artanis's format.

    It handles the packaging of a model object and its metadata into a binary format, including a header for protocol
    and compression information, and delegating the core serialization to the appropriate protocol and model-specific
    serializers.
    """

    _header_format: t.Final[str] = "!I I Q"
    _header_size: t.Final[int] = struct.calcsize(_header_format)

    @t.overload
    @classmethod
    def dump(
        cls,
        m: t.Any,
        f: t.BinaryIO,
        /,
        *,
        protocol: types.ProtocolVersion = 1,
        compression: types.Compression = "zstd",
        model_id: str | uuid.UUID | None = None,
        timestamp: datetime.datetime | None = None,
        params: dict[str, t.Any] | None = None,
        metrics: dict[str, t.Any] | None = None,
        extra: dict[str, t.Any] | None = None,
        artifacts: Artifacts | None = None,
        **kwargs,
    ) -> None: ...
    @t.overload
    @classmethod
    def dump(
        cls,
        m: t.Any,
        /,
        *,
        path: str | os.PathLike | pathlib.Path,
        protocol: types.ProtocolVersion = 1,
        compression: types.Compression = "zstd",
        model_id: str | uuid.UUID | None = None,
        timestamp: datetime.datetime | None = None,
        params: dict[str, t.Any] | None = None,
        metrics: dict[str, t.Any] | None = None,
        extra: dict[str, t.Any] | None = None,
        artifacts: Artifacts | None = None,
        **kwargs,
    ) -> None: ...
    @classmethod
    def dump(
        cls,
        m: t.Any,
        f: t.BinaryIO | None = None,
        /,
        *,
        path: str | os.PathLike | pathlib.Path | None = None,
        protocol: types.ProtocolVersion = 1,
        compression: types.Compression = "zstd",
        model_id: str | uuid.UUID | None = None,
        timestamp: datetime.datetime | None = None,
        params: dict[str, t.Any] | None = None,
        metrics: dict[str, t.Any] | None = None,
        extra: dict[str, t.Any] | None = None,
        artifacts: Artifacts | None = None,
        **kwargs,
    ) -> None:
        """Serialize an ML model using Artanis format to bytes stream.

        :param m: The ML model.
        :param s: The bytes stream for dumping the model artifact.
        :param path: The file path where the model artifact will be stored.
        :param protocol: Serialization protocol version.
        :param compression: Compression format.
        :param model_id: The model ID.
        :param timestamp: The model timestamp.
        :param params: The model parameters.
        :param metrics: The model metrics.
        :param extra: The model extra data.
        :param artifacts: The model artifacts.
        :param kwargs: Keyword arguments passed to library dump method.
        """
        if f is None and path is None:
            raise ValueError("Either a 'stream' or a 'path' needs to be provided")
        elif f is not None and path is not None:
            raise ValueError("Parameters 'stream' and 'path' are mutually exclusive")
        elif f is not None:
            managed_stream = False
        else:
            managed_stream = True
            f = pathlib.Path(str(path)).open("wb")

        p = Protocol.from_version(protocol)
        c = Compression(compression)

        body = p.dump(
            ModelArtifact.from_model(
                m,
                model_id=model_id,
                timestamp=timestamp,
                params=params,
                metrics=metrics,
                extra=extra,
                artifacts=artifacts,
            ),
            compression=c,
            **kwargs,
        )
        header = struct.pack(cls._header_format, protocol, c.format.value, len(body))

        try:
            f.write(b"".join((header, body)))
        finally:
            if managed_stream:
                f.flush()
                f.close()

    @t.overload
    @classmethod
    def load(cls, f: t.BinaryIO, /, **kwargs) -> ModelArtifact: ...
    @t.overload
    @classmethod
    def load(cls, /, *, path: str | os.PathLike | pathlib.Path, **kwargs) -> ModelArtifact: ...
    @classmethod
    def load(
        cls, f: t.BinaryIO | None = None, /, *, path: str | os.PathLike | pathlib.Path | None = None, **kwargs
    ) -> ModelArtifact:
        """Deserialize a ML model using Artanis format from a bytes stream.

        :param s: The bytes stream for loading the model artifact.
        :param path: The file path where the model artifact is stored.
        :return: Model artifact.
        """
        if f is None and path is None:
            raise ValueError("Either a 'stream' or a 'path' needs to be provided")
        elif f is not None and path is not None:
            raise ValueError("Parameters 'stream' and 'path' are mutually exclusive")
        elif f is not None:
            managed_stream = False
        else:
            managed_stream = True
            f = pathlib.Path(str(path)).open("rb")

        try:
            protocol, compression, body_size = struct.unpack(cls._header_format, f.read(cls._header_size))

            p = Protocol.from_version(protocol)
            c = Compression(compression)
            artifact = p.load(f.read(body_size), compression=c)
        finally:
            if managed_stream:
                f.flush()
                f.close()

        if (
            serializer_version := ModelSerializer.from_lib(artifact.meta.framework.lib).version()
        ) != artifact.meta.framework.version:  # noqa
            warnings.warn(
                f"Model was built using {artifact.meta.framework.lib} '{artifact.meta.framework.version}' but "
                f"detected version '{serializer_version}' installed. This may cause unexpected behavior.",
                exceptions.FrameworkVersionWarning,
            )

        return artifact


dump = Serializer.dump
load = Serializer.load
