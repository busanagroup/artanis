__all__ = ["Context"]

from artanis.asgi import types, routing
from artanis.asgi.http import Request, Response
from artanis.asgi.websockets import WebSocket
from artanis.injection import context


class Context(context.Context):
    scope = context.Field(types.Scope)
    receive = context.Field(types.Receive)
    send = context.Field(types.Send)
    exc = context.Field(Exception, required=False)
    app = context.Field(types.App)
    route = context.Field(routing.BaseRoute)
    request = context.Field(Request, hashable=False)
    response = context.Field(Response, required=False)
    websocket = context.Field(WebSocket, hashable=False)
    websocket_message = context.Field(types.Message, required=False)
    websocket_encoding = context.Field(types.Encoding, required=False)
    websocket_code = context.Field(types.Code, required=False)
