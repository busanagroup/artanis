"""Async LDAP client library.

Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "{}"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright 2015-2016 Nikolai Novik

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.


Example:
    import aioldap3

    conn = aioldap.LDAPConnection(Server(host='localhost', port=389))
    await conn.bind(
        bind_dn='admin',
        bind_pw='password,
    )

    print(await conn.whoami())

    dn = user_entry('modify', ldap_params['test_ou1'])
    await conn.add(
        dn=dn,
        object_class='inetOrgPerson',
        attributes={
            'description': 'some desc',
            'cn': 'some_user',
            'sn': 'some user',
            'employeeType': ['type1', 'type2']}
    )

    await conn.modify(
        dn=dn,
        changes={
            'sn': [('MODIFY_REPLACE', 'some other user')],
            'employeeType': [
                ('MODIFY_ADD', 'type3'),
                ('MODIFY_DELETE', 'type1'),
            ]
        }
    )

    # Now search for user
    async for user in conn.search(
            dn, search_filter='(uid=*)', search_scope='BASE', attributes='*'):
        assert user['dn'] == dn

"""

from __future__ import annotations

import asyncio
import asyncio.sslproto
import logging
import ssl
from abc import ABC, abstractmethod
from contextlib import suppress
from copy import deepcopy
from dataclasses import dataclass, field
from types import TracebackType
from typing import TYPE_CHECKING, Any, AsyncGenerator, Callable, Literal, cast

from ldap3 import PLAIN
from ldap3.operation.add import add_operation
from ldap3.operation.bind import bind_operation, bind_response_to_dict_fast
from ldap3.operation.delete import delete_operation
from ldap3.operation.extended import (
    extended_operation,
    extended_response_to_dict_fast,
)
from ldap3.operation.modify import modify_operation
from ldap3.operation.search import (
    search_operation,
    search_result_entry_response_to_dict_fast,
    search_result_reference_response_to_dict_fast,
)
from ldap3.protocol.convert import build_controls_list
from ldap3.protocol.rfc2696 import paged_search_control
from ldap3.protocol.rfc3062 import PasswdModifyRequestValue
from ldap3.protocol.rfc4511 import (
    AuthenticationChoice,
    BindRequest,
    ExtendedRequest,
    LDAPMessage,
    MessageID,
    ProtocolOp,
    SaslCredentials,
    Simple,
    UnbindRequest,
    Version,
)
from ldap3.protocol.rfc4512 import SchemaInfo
from ldap3.strategy.base import BaseStrategy  # Consider moving this to utils
from ldap3.utils.asn1 import (
    decode_message_fast,
    ldap_result_to_dict_fast, encode,
)
from ldap3.utils.conv import to_unicode
from ldap3.utils.dn import safe_dn
from ldap3.utils.ntlm import NtlmClient
from pyasn1.codec.ber import encoder
from pyasn1.type.base import Asn1Item
from pyasn1.type.univ import Sequence

if TYPE_CHECKING:
    from _typeshed import ReadableBuffer
__all__ = [
    "Server",
    "LDAPResponse",
    "LDAPClientProtocol",
    "LDAPConnection",
    "LDAPError",
    "LDAPBindError",
    "LDAPStartTlsError",
    "LDAPChangeError",
    "LDAPModifyError",
    "LDAPDeleteError",
    "LDAPAddError",
    "LDAPExtendedError",
    "OperationNotSupportedError",
]

logger = logging.getLogger("aioldap")

EntryType = list[dict[str, str | bytes | list[bytes] | dict[str, list[bytes]]]]


class LDAPError(Exception):  # noqa: D101
    pass


class LDAPBindError(LDAPError):  # noqa: D101
    pass


class LDAPStartTlsError(LDAPError):  # noqa: D101
    pass


class LDAPChangeError(LDAPError):  # noqa: D101
    pass


class LDAPModifyError(LDAPError):  # noqa: D101
    pass


class LDAPDeleteError(LDAPError):  # noqa: D101
    pass


class LDAPAddError(LDAPError):  # noqa: D101
    pass


class LDAPExtendedError(LDAPError):  # noqa: D101
    pass


class OperationNotSupportedError(Exception):  # noqa: D101
    def __init__(self, code: str | int) -> None:
        """Set a new message."""
        super().__init__(
            f"This LDAP operation with code {code} is not supported"
        )


@dataclass(frozen=True)
class SearchResult:
    entries: EntryType
    refs: list[Any]
    pagination: bool | None


class SaslCreds(ABC):
    """Base class for SASL credentials."""

    @property
    @abstractmethod
    def sasl_mechanism(
        self,
    ) -> Literal["PLAIN", "DIGEST-MD5", "GSSAPI", "EXTERNAL"]:
        """Return the SASL mechanism name."""

    @abstractmethod
    def encode(self) -> str:
        """Encode credentials for SASL authentication."""


class PlainSaslCreds(SaslCreds):
    """SASL credentials implementation for PLAIN authentication."""

    sasl_mechanism: Literal["PLAIN"] = PLAIN

    def __init__(self, username: str, password: str) -> None:
        """Initialize SASL credentials.

        :param username: Username for authentication
        :param password: Password for authentication
        """
        self.username = username
        self.password = password

    def encode(self) -> str:
        """Encode credentials for SASL authentication.

        :return: Credentials string in format
            "username\x00username\x00password"
        """
        return f"{self.username}\x00{self.username}\x00{self.password}"


@dataclass
class Server:
    """Server data container."""

    host: str
    port: int = 389
    use_ssl: bool = False
    ssl_context: ssl.SSLContext | None = field(
        default_factory=ssl.create_default_context
    )
    timeout: float | int | None = None
    version: Literal[2, 3] = 3

    def __post_init__(self) -> None:
        """Set ssl context."""
        self.ssl_context = self.ssl_context if self.use_ssl else None


class LDAPResponse:
    """LDAPResponse container."""

    data: dict[str, Any]
    entries: EntryType
    exception: BaseException | None = None

    def __init__(self, onfinish: Callable[[], None] | None = None) -> None:
        """Set callback."""
        self._onfinish = onfinish
        self.started = asyncio.Event()
        self.finished = asyncio.Event()
        self.refs: list[Any] = []
        self.additional: dict[str, Any] = {}
        self.entries = []

    async def wait(self) -> None:
        """Wait for response."""
        await self.finished.wait()
        try:
            if callable(self._onfinish):
                self._onfinish()
        finally:
            if self.exception:
                raise self.exception


class LDAPClientProtocol(asyncio.Protocol):
    """Protocol for client conn."""

    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        """Set loop and transport."""
        self.loop = loop

        self.transport: asyncio.Transport = None  # type: ignore
        self._original_transport: asyncio.Transport = None  # type: ignore
        self._using_tls = False
        self._tls_event = asyncio.Event()
        self._is_bound = False

        self.unprocessed = b""
        self.messages: list[bytes] = []

        self.responses: dict[int, LDAPResponse] = {}

    def send(self, msg: Sequence, unbind: bool = False) -> LDAPResponse:
        """Send LDAP message."""
        msg_id: int = int(msg["messageID"])

        if unbind:
            msg_id = -1

        response = LDAPResponse(
            onfinish=lambda: self._remove_msg_id_response(msg_id)
        )
        self.responses[msg_id] = response

        payload = encode(msg)

        logger.debug(f"Sending request id {msg_id}")

        self.transport.write(payload)

        logger.debug(f"Sent request id {msg_id}")
        response.started.set()

        return response

    def _remove_msg_id_response(self, msg_id: int) -> None:
        """Remove msg from responses."""
        with suppress(KeyError):
            del self.responses[msg_id]

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        """Set transport."""
        if self._original_transport is None:
            self.transport = transport  # type: ignore
        else:
            self._using_tls = True
            self._tls_event.set()

    def eof_received(self) -> bool:
        """Check if conn meet eof."""
        if self._using_tls:
            return False
        return super().eof_received()  # type: ignore

    def data_received(self, data: bytes) -> None:  # TODO: decompose
        """Check if message is full."""
        logger.debug(f"data_received: len {len(data)}")
        self.unprocessed += data

        if len(data) <= 0:
            return

        length = BaseStrategy.compute_ldap_message_size(self.unprocessed)
        logger.debug(f"data_received: msg_length {length}")

        while len(self.unprocessed) >= length != -1:
            logger.debug(
                "data_received: appended msg, "
                f"len: {len(self.unprocessed[:length])}"
            )
            self.messages.append(self.unprocessed[:length])
            self.unprocessed = self.unprocessed[length:]

            length = BaseStrategy.compute_ldap_message_size(self.unprocessed)
            logger.debug(f"data_received: msg_length {length}")

        while self.messages:
            msg = self.messages.pop(0)

            try:
                msg_asn = decode_message_fast(msg)
            except Exception as exc:
                logger.warning(
                    "data_received: Caught exception "
                    f"whilst decoding message {exc}"
                )
                continue
            msg_id = msg_asn["messageID"]
            logger.debug(f"data_received: Decoded message, id {msg_id}")
            is_list = False
            finish = False

            msg_additional = {}
            msg_refs = None

            if msg_asn["protocolOp"] == 1:
                # Bind request, only 1, finished after this
                msg_data = bind_response_to_dict_fast(msg_asn["payload"])
                msg_log = f"data_received: id {msg_id}, bind"
                finish = True

            elif msg_asn["protocolOp"] == 4:  # Search response, can be N,
                is_list = True
                msg_data = search_result_entry_response_to_dict_fast(
                    msg_asn["payload"], None, None, False
                )
                msg_log = f"data_received: id {msg_id}, search response"

            elif msg_asn["protocolOp"] == 5:  # Search result done
                finish = True
                msg_data = None  # Clear msg_data

                # Get default doesnt work here
                controls = msg_asn.get("controls")
                if not controls:
                    controls = []

                controls = [
                    BaseStrategy.decode_control_fast(control[3])
                    for control in controls
                ]
                msg_additional = {
                    "asn": msg_asn,
                    "controls": {item[0]: item[1] for item in controls},
                }
                msg_log = f"data_received: id {msg_id}, search done"

            # Modify response, could merge with 9,11
            elif msg_asn["protocolOp"] == 7:
                msg_data = ldap_result_to_dict_fast(msg_asn["payload"])
                msg_log = f"data_received: id {msg_id}, modify response"
                finish = True

            elif msg_asn["protocolOp"] == 9:  # Add response
                msg_data = ldap_result_to_dict_fast(msg_asn["payload"])
                msg_log = f"data_received: id {msg_id}, add response"
                finish = True

            elif msg_asn["protocolOp"] == 11:  # Del response
                msg_data = ldap_result_to_dict_fast(msg_asn["payload"])
                msg_log = f"data_received: id {msg_id}, del response"
                finish = True

            elif msg_asn["protocolOp"] == 19:
                msg_data = None
                msg_refs = search_result_reference_response_to_dict_fast(
                    msg_asn["payload"]
                )
                msg_log = f"data_received: id {msg_id}, refs response"

            elif msg_asn["protocolOp"] == 24:
                msg_data = extended_response_to_dict_fast(msg_asn["payload"])
                msg_log = f"data_received: id {msg_id}, extended response"
                finish = True
            else:
                raise OperationNotSupportedError(msg_asn["protocolOp"])

            logger.debug(msg_log)

            if msg_id not in self.responses:
                # TODO raise some flags, this aint good
                logger.warning(f"data_received: unknown msg id {msg_id}")
                continue

            # If we have data to store
            if msg_data:
                # If data is a singular item
                if not is_list:
                    self.responses[msg_id].data = msg_data
                else:
                    # If data is an element of a continiously expanding set
                    self.responses[msg_id].entries.append(msg_data)

            if msg_refs:
                self.responses[msg_id].refs.append(msg_refs)

            if msg_additional:
                self.responses[msg_id].additional = msg_additional

            # Mark request as done
            if finish:
                self.responses[msg_id].finished.set()
                logger.debug(f"data_received: id {msg_id}, marked finished")

    def connection_lost(self, exc: Exception | None) -> None:
        """Check if conn lost."""
        logger.debug("Connection lost")

        self._is_bound = False
        for key, response in self.responses.items():
            if key != "unbind":
                response.exception = ConnectionResetError(
                    "LDAP Server dropped the connection"
                )
            response.finished.set()

        if self._original_transport is not None:
            self._original_transport.close()
        super().connection_lost(exc)
        self.transport = None  # type: ignore

    async def start_tls(self, ctx: ssl.SSLContext) -> None:
        """Run TLS."""
        ssl_proto = asyncio.sslproto.SSLProtocol(
            loop=self.loop,
            app_protocol=self,
            sslcontext=ctx,
            waiter=asyncio.Future(),
            server_side=False,
        )

        self._original_transport = self.transport
        self._original_transport.set_protocol(ssl_proto)

        self.transport = ssl_proto._app_transport
        ssl_proto.connection_made(self._original_transport)

        # Wait for handshake
        await self._tls_event.wait()

    @property
    def is_bound(self) -> bool:
        """Check if resp is bound."""
        return self._is_bound

    @is_bound.setter
    def is_bound(self, value: bool) -> None:
        self._is_bound = value

    @staticmethod
    def encapsulate_ldap_message(
        message_id: int,
        obj_name: str,
        obj: str | BindRequest | UnbindRequest | ExtendedRequest | NtlmClient,
        controls: list[str] | None = None,
    ) -> LDAPMessage:
        """Create LDAP message."""
        ldap_message = LDAPMessage()
        ldap_message["messageID"] = MessageID(message_id)
        ldap_message["protocolOp"] = ProtocolOp().setComponentByName(
            obj_name, obj
        )

        msg_controls = build_controls_list(controls)
        if msg_controls:
            ldap_message["controls"] = msg_controls

        return ldap_message


class LDAPConnection:
    """Async connector."""

    _proto: LDAPClientProtocol
    _socket: asyncio.Transport

    def __init__(
        self,
        server: Server,
        user: str | None = None,
        password: str | None = None,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        """Set server, user and pw."""
        self._responses: dict[str, LDAPResponse] = {}
        self._msg_id = 0
        self.loop = loop or asyncio.get_running_loop()

        self.server = server
        self.bind_dn = user
        self.bind_pw = password

    async def __aenter__(self) -> LDAPConnection:
        """Do autobind."""
        await self.bind()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Do unbind."""
        await self.unbind()
        self.close()

    def __del__(self) -> None:
        """Close conn."""
        self.close()

    def close(self) -> None:
        """Close conn."""
        if hasattr(self, "_proto"):
            with suppress(Exception):
                if self._proto._original_transport:
                    self._proto._original_transport.close()

            with suppress(Exception):
                if self._proto.transport:
                    self._proto.transport.close()

        if hasattr(self, "_socket") is not None:
            with suppress(Exception):
                self._socket.close()

        with suppress(AttributeError):
            del self._proto
            del self._socket

    @property
    def _next_msg_id(self) -> int:
        self._msg_id += 1
        return self._msg_id

    async def _create_connection(
        self,
        timeout: int | float | None = None,
        ssl_context: ssl.SSLContext | None = None,
    ) -> None:
        """Create connection with timeout handling."""
        create_conn = self.loop.create_connection(
            lambda: LDAPClientProtocol(self.loop),
            self.server.host,
            self.server.port,
            ssl=ssl_context,
        )

        timeout = timeout or self.server.timeout
        if timeout is not None:
            self._socket, self._proto = await asyncio.wait_for(
                create_conn,
                timeout=timeout,
            )
        else:
            self._socket, self._proto = await create_conn

    async def bind(
        self,
        bind_dn: str | None = None,
        bind_pw: str | None = None,
        method: Literal["ANONYMOUS", "SIMPLE", "SASL", "NTLM"] = "SIMPLE",
        timeout: int | float | None = None,
        sasl_credentials: SaslCreds | None = None,
    ) -> None:
        """Bind to LDAP server.

        Creates a connection to the LDAP server if there isnt one

        :param bind_dn: Bind DN
        :param bind_pw: Bind password
        :param method: Authentication method (ANONYMOUS, SIMPLE, SASL, NTLM)
        :param timeout: Timeout for bind operation in seconds
        :param sasl_credentials: SASL credentials
            object implementing SaslCreds interface
        :raises LDAPBindError: If credentials are invalid
        """
        # Create proto if its not created already
        if not hasattr(self, "_proto") or self._proto.transport.is_closing():
            await self._create_connection(
                timeout,
                self.server.ssl_context,
            )

        if bind_dn is None:
            bind_dn = self.bind_dn
        if bind_pw is None:
            bind_pw = self.bind_pw

        # If bind_dn is still None or '' then set up for anon bind
        if not bind_dn:
            bind_dn = ""
            bind_pw = ""

        # TODO check if already bound

        # Create bind packet
        if method == "SIMPLE":
            bind_req = BindRequest()
            bind_req["version"] = Version(3)
            bind_req["name"] = bind_dn
            bind_req["authentication"] = (
                AuthenticationChoice().setComponentByName(
                    "simple",
                    Simple(bind_pw),
                )
            )

        elif method == "NTLM":
            domain_name, user_name = bind_dn.split("\\", 1)
            ntlm_client = NtlmClient(domain_name, user_name, bind_pw)

            # as per https://msdn.microsoft.com/en-us/library/cc223501.aspx
            # send a sicilyPackageDiscovery request (in the bindRequest)
            bind_req = bind_operation(
                self.server.version,
                "SICILY_PACKAGE_DISCOVERY",
                ntlm_client,
            )

        elif method == "SASL":
            if not sasl_credentials:
                raise LDAPBindError(
                    "SASL credentials must be provided for SASL authentication"
                )

            bind_req = BindRequest()
            bind_req["version"] = Version(3)
            bind_req["name"] = bind_dn

            # Create SASL credentials
            sasl_creds = SaslCredentials()
            sasl_creds["mechanism"] = sasl_credentials.sasl_mechanism
            sasl_creds["credentials"] = sasl_credentials.encode()

            bind_req["authentication"] = (
                AuthenticationChoice().setComponentByName(
                    "sasl",
                    sasl_creds,
                )
            )

        else:
            raise LDAPBindError("Unsupported Authentication Method")

        # As were binding, msg ID should be 1
        self._msg_id = 0

        # Get next msg ID
        msg_id = self._next_msg_id

        # Generate ASN1 form of LDAP bind request
        ldap_msg = LDAPClientProtocol.encapsulate_ldap_message(
            msg_id, "bindRequest", bind_req
        )

        # Send request to LDAP server, as multiple LDAP queries
        # can run simultaneously, were given an object to wait on
        # which will return once done.
        resp = self._proto.send(ldap_msg)

        if timeout is not None:
            await asyncio.wait_for(resp.wait(), timeout)
        else:
            await resp.wait()

        # If the result is non-zero for a bind, we got some invalid creds yo
        if resp.data["result"] != 0:
            raise LDAPBindError("Invalid Credentials")

        # Ok we got success, this is used
        # in other places as a guard if your not bound
        self._proto.is_bound = True

    async def search(
        self,
        search_base: str,
        search_filter: str,
        search_scope: str = "SUBTREE",
        dereference_aliases: str = "ALWAYS",
        attributes: str | list[str] | None = None,
        size_limit: int = 0,
        time_limit: int = 0,
        types_only: bool = False,
        auto_escape: bool = True,
        auto_encode: bool = True,
        schema: SchemaInfo | None = None,
        validator: Callable[[str], bool] | None = None,
        check_names: bool = False,
        cookie: bool | None = None,
        timeout: int | None = None,
        get_operational_attributes: bool = False,
        page_size: int = 0,
    ) -> SearchResult:
        """Do search in DIT.

        :param str search_base: base DN
        :param str search_filter: LDAP filter
        :param str search_scope: scope, defaults to 'SUBTREE'
        :param str dereference_aliases: deref, defaults to 'ALWAYS'
        :param Optional[Union[str, List[str]]] attributes:
            attrs to include, defaults to None
        :param int size_limit: search limit, defaults to 0
        :param int time_limit: request timeout on server, defaults to 0
        :param bool types_only: return only types, defaults to False
        :param bool auto_escape: auto esc, defaults to True
        :param bool auto_encode: encode msg, defaults to True
        :param SchemaInfo schema: schema, defaults to None
        :param Callable[[str], bool] validator:
            custom validator, defaults to None
        :param bool check_names: validate names, defaults to False
        :param bool cookie: use cookie, defaults to None
        :param Optional[int] timeout:
            request timeout on client side, defaults to None
        :param bool get_operational_attributes: defaults to False
        :param int page_size: defaults to 0
        :raises LDAPBindError: on invalid creds
        :return Dict[str, Any]: search result.
        """
        if not self.is_bound:
            raise LDAPBindError("Must be bound")

        if search_base:
            search_base = safe_dn(search_base)

        if not attributes:
            attributes = ["1.1"]
        elif attributes == "*":
            attributes = ["*"]
        if isinstance(attributes, str):
            attributes = [attributes]

        if get_operational_attributes and isinstance(attributes, list):
            attributes.append("+")

        controls = []
        if page_size:
            controls.append(paged_search_control(False, page_size, cookie))
        if not controls:
            controls = None  # type: ignore

        search_req = search_operation(
            search_base,
            search_filter,
            search_scope,
            dereference_aliases,
            attributes,
            size_limit,
            time_limit,
            types_only,
            auto_escape=auto_escape,
            auto_encode=auto_encode,
            schema=schema,
            validator=validator,
            check_names=check_names,
        )

        ldap_msg = LDAPClientProtocol.encapsulate_ldap_message(
            self._next_msg_id, "searchRequest", search_req, controls=controls
        )

        resp = self._proto.send(ldap_msg)

        if timeout:
            await asyncio.wait_for(resp.wait(), timeout)
        else:
            await resp.wait()

        try:
            cookie = resp.additional["controls"]["1.2.840.113556.1.4.319"][
                "value"
            ]["cookie"]
        except KeyError:
            cookie = None

        return SearchResult(
            entries=resp.entries,
            refs=resp.refs,
            pagination=cookie,
        )

    async def paged_search(
        self,
        search_base: str,
        search_filter: str,
        search_scope: str = "SUBTREE",
        dereference_aliases: str = "ALWAYS",
        attributes: str | list[str] | None = None,
        size_limit: int = 0,
        time_limit: int = 0,
        types_only: bool = False,
        auto_escape: bool = True,
        auto_encode: bool = True,
        schema: SchemaInfo | None = None,
        validator: Callable[[str], bool] | None = None,
        check_names: bool = False,
        timeout: int | None = None,
        get_operational_attributes: bool = False,
        page_size: int = 500,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Paginate search.

        Do search in DIT.

        :param str search_base: base DN
        :param str search_filter: LDAP filter
        :param str search_scope: scope, defaults to 'SUBTREE'
        :param str dereference_aliases: deref, defaults to 'ALWAYS'
        :param Optional[Union[str, List[str]]] attributes:
            attrs to include, defaults to None
        :param int size_limit: search limit, defaults to 0
        :param int time_limit: request timeout on server, defaults to 0
        :param bool types_only: return only types, defaults to False
        :param bool auto_escape: auto esc, defaults to True
        :param bool auto_encode: encode msg, defaults to True
        :param SchemaInfo schema: schema, defaults to None
        :param Callable[[str], bool] validator:
            custom validator, defaults to None
        :param bool check_names: validate names, defaults to False
        :param bool cookie: use cookie, defaults to None
        :param Optional[int] timeout:
            request timeout on client side, defaults to None
        :param bool get_operational_attributes: defaults to False
        :param int page_size: defaults to 0
        :raises LDAPBindError: on invalid creds
        :return Dict[str, Any]: search result.
        """
        if not self.is_bound:
            raise LDAPBindError("Must be bound")

        cookie: bool | None = True  # True so loop runs once
        while cookie is not None and cookie != b"":
            response = await self.search(
                search_base,
                search_filter,
                search_scope=search_scope,
                dereference_aliases=dereference_aliases,
                attributes=attributes,
                size_limit=size_limit,
                time_limit=time_limit,
                types_only=types_only,
                auto_escape=auto_escape,
                auto_encode=auto_encode,
                schema=schema,
                validator=validator,
                check_names=check_names,
                timeout=timeout,
                get_operational_attributes=get_operational_attributes,
                page_size=page_size,
                cookie=None if cookie is True else cookie,
            )

            while response.entries:
                yield response.entries.pop()

            cookie = response.pagination

    async def unbind(self) -> None:
        """Unbind session.

        Send and wait, when unbinding, the server terminates
        the connection, so when it does that, the
        asyncio.Event for the unbind request is set().
        As there is no response from the server, we get
        no msg_id, therefore we tell send() its a special case.
        """
        if not self.is_bound:
            return  # Exit quickly if were already unbound

        # Create unbind request
        unbind_req = UnbindRequest()
        msg_id = self._next_msg_id

        self._unbind_in_progress = True

        # Generate final LDAP ASN message
        ldap_msg = LDAPClientProtocol.encapsulate_ldap_message(
            msg_id, "unbindRequest", unbind_req
        )
        resp = self._proto.send(ldap_msg, unbind=True)

        # Unbind is a special case, we dont get a response
        with suppress(asyncio.TimeoutError):
            await asyncio.wait_for(resp.wait(), timeout=0)

        # Cleanup transport and protocol
        if not (
            self._proto.transport is None or self._proto.transport.is_closing()
        ):
            del self._proto

    async def start_tls(
        self,
        ctx: ssl.SSLContext | None = None,
        timeout: int | float | None = None,
    ) -> None:
        """Start tls protocol.

        :param ctx: Optional SSL context.
        :param timeout: Optional timeout in seconds.
        :raises LDAPStartTlsError: On TLS related errors or connection timeout.
        """
        if hasattr(self, "_proto") or self._proto.transport.is_closing():
            await self._create_connection(timeout)

        # Get SSL context from server obj, if
        # it's not provided, it'll be the default one

        resp = await self.extended("1.3.6.1.4.1.1466.20037")

        if resp.data["description"] != "success":
            raise LDAPStartTlsError(
                "Server doesnt want us to use TLS. {}".format(
                    resp.data.get("message")
                )
            )

        await self._proto.start_tls(
            ctx or cast("ssl.SSLContext", self.server.ssl_context)
        )

    async def extended(
        self,
        request_name: str,
        request_value: Asn1Item | ReadableBuffer | None = None,
        controls: list[str] | None = None,
        no_encode: bool | None = None,
    ) -> Any:
        """Perform an extended operation."""
        # Create unbind request
        extended_req = extended_operation(
            request_name, request_value, no_encode=no_encode
        )
        msg_id = self._next_msg_id

        # Generate final LDAP ASN message
        ldap_msg = LDAPClientProtocol.encapsulate_ldap_message(
            msg_id, "extendedReq", extended_req, controls=controls
        )

        resp = self._proto.send(ldap_msg)
        await resp.wait()

        return resp

    async def modify(
        self,
        dn: str,
        changes: dict[str, list[tuple[str]]],
        controls: list[str] | None = None,
        auto_encode: bool = True,
    ) -> None:
        """Modify attributes of entry.

        - changes is a dictionary in the form {'attribute1': change),
            'attribute2': [change, change, ...], ...}
        - change is (operation, [value1, value2, ...])
        - operation is
            0 (MODIFY_ADD),
            1 (MODIFY_DELETE),
            2 (MODIFY_REPLACE),
            3 (MODIFY_INCREMENT)
        """
        dn = safe_dn(dn)

        if not isinstance(changes, dict):
            raise LDAPChangeError("Changes is not a dict")

        if not changes:
            raise LDAPChangeError("Changes dict cannot be empty")

        modify_req = modify_operation(
            dn, changes, auto_encode, None, validator=None, check_names=False
        )
        msg_id = self._next_msg_id

        # Generate final LDAP ASN message
        ldap_msg = LDAPClientProtocol.encapsulate_ldap_message(
            msg_id, "modifyRequest", modify_req, controls=controls
        )

        resp = self._proto.send(ldap_msg)
        await resp.wait()

        if resp.data["result"] != 0:
            raise LDAPModifyError(
                "Failed to modify dn {}. Msg {} {} {}".format(
                    dn,
                    resp.data["result"],
                    resp.data.get("message"),
                    resp.data.get("description"),
                )
            )

    async def delete(
        self,
        dn: str,
        controls: list[str] | None = None,
        ignore_no_exist: bool = False,
    ) -> None:
        """Delete the entry identified by the DN from the DIB."""
        dn = safe_dn(dn)

        del_req = delete_operation(dn)
        msg_id = self._next_msg_id

        # Generate final LDAP ASN message
        ldap_msg = LDAPClientProtocol.encapsulate_ldap_message(
            msg_id, "delRequest", del_req, controls=controls
        )

        resp = self._proto.send(ldap_msg)
        await resp.wait()

        if resp.data["result"] != 0 and not (
            ignore_no_exist and resp.data["result"] == 32
        ):
            raise LDAPDeleteError(
                "Failed to modify dn {}. Msg {} {} {}".format(
                    dn,
                    resp.data["result"],
                    resp.data.get("message"),
                    resp.data.get("description"),
                )
            )

    async def add(
        self,
        dn: str,
        object_class: list[str] | str | None = None,
        attributes: dict[str, list[str] | str] | None = None,
        controls: list[str] | None = None,
        auto_encode: bool = True,
        timeout: int | None = None,
    ) -> None:
        """Add dn to the DIT.

        object_class is None, a class name or a list
        of class names.

        Attributes is a dictionary in the form 'attr': 'val' or 'attr':
        ['val1', 'val2', ...] for multivalued attributes
        """
        # dict could change when adding objectClass values
        _attributes = deepcopy(attributes)
        dn = safe_dn(dn)

        attr_object_class = []

        if object_class is not None:
            if isinstance(object_class, str):
                attr_object_class.append(object_class)
            else:
                attr_object_class.extend(object_class)

        # Look through attributes to see if object classes are specified there
        object_class_attr_name = ""
        if not _attributes:
            _attributes = {}

        for attr in _attributes:
            if attr.lower() == "objectclass":
                object_class_attr_name = attr

                obj_class_val = _attributes[object_class_attr_name]
                if isinstance(obj_class_val, str):
                    attr_object_class.append(obj_class_val)
                else:
                    attr_object_class.extend(obj_class_val)
                break

        if not object_class_attr_name:
            object_class_attr_name = "objectClass"

        # So now we have attr_object_class,
        # which contains any passed in object classes
        # and any we've found in attributes.
        # Converts objectclass to unicode
        # in case of bytes value, also removes dupes
        attr_object_class = list(
            {to_unicode(object_class) for object_class in attr_object_class}
        )
        _attributes[object_class_attr_name] = attr_object_class

        add_request = add_operation(
            dn,
            _attributes,
            auto_encode,
            None,
            validator=None,
            check_names=False,
        )
        msg_id = self._next_msg_id

        # Generate final LDAP ASN message
        ldap_msg = LDAPClientProtocol.encapsulate_ldap_message(
            msg_id,
            "addRequest",
            add_request,
            controls=controls,
        )

        resp = self._proto.send(ldap_msg)
        if timeout:
            await asyncio.wait_for(resp.wait(), timeout)
        else:
            await resp.wait()

        if resp.data["result"] != 0:
            raise LDAPAddError(
                "Failed to modify dn {}. Msg {} {} {}".format(
                    dn,
                    resp.data["result"],
                    resp.data.get("message"),
                    resp.data.get("description"),
                )
            )

    async def whoami(self) -> str:
        """Get WhoAmI extended result."""
        resp = await self.extended("1.3.6.1.4.1.4203.1.11.3")

        if resp.data["result"] != 0:
            raise LDAPExtendedError(
                "Failed to perform extended query. Msg {} {} {}".format(
                    resp.data["result"],
                    resp.data.get("message"),
                    resp.data.get("description"),
                )
            )

        result = resp.data.get("responseValue")
        if isinstance(result, bytes):
            result = result.decode()

        return result

    @property
    def is_bound(self) -> bool:
        """Check if bound."""
        return hasattr(self, "_proto") and self._proto.is_bound

    async def get_root_dse(self) -> SearchResult:
        """Get rootDSE from server."""
        return await self.search(
            "",
            "(objectClass=*)",
            search_scope="BASE",
            attributes="*",
        )

    async def modify_password(
        self,
        new_password: str,
        user_dn: str,
        old_password: str,
    ) -> None:
        """Modify user password using LDAP password modify extended operation.

        This method uses the LDAP password modify extended operation (RFC 3062)
        to change a user's password. The operation requires:
        1. An authenticated connection
        2. The user's DN
        3. The current password
        4. The new password to set

        :param new_password: The new password to set
        :param user_dn: The DN of the user whose password to change
        :param old_password: The current password of the user
        :raises LDAPBindError: If not bound
        :raises LDAPExtendedError: If password modification fails
        """
        if not self.is_bound:
            logger.error("Need bound LDAPConnection to modify password")
            raise LDAPBindError("Must be bound to modify password")

        request_value = PasswdModifyRequestValue()
        request_value.setComponentByName("userIdentity", user_dn)
        request_value.setComponentByName("oldPasswd", old_password)
        request_value.setComponentByName("newPasswd", new_password)

        psw_change_oid: Literal["1.3.6.1.4.1.4203.1.11.1"] = (
            "1.3.6.1.4.1.4203.1.11.1"
        )

        logger.debug(f"Attempting to modify password for user: {user_dn}")

        res = await self.extended(
            psw_change_oid,
            encoder.encode(request_value),
        )

        if res.data["result"] != 0:
            error_msg = (
                f"Password modification failed: "
                f"{res.data.get('message', 'Unknown error')} "
                f"(result code: {res.data.get('result')}, "
                f"description: {res.data.get('description')})"
            )
            logger.error(error_msg)
            raise LDAPExtendedError(error_msg)

        logger.info(f"Password successfully modified for user: {user_dn}")
