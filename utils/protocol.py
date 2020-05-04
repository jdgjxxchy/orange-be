#!/usr/bin/env python
# encoding: utf-8

from sanic.websocket import WebSocketProtocol
from sanic.exceptions import InvalidUsage

from websockets import (  # type: ignore
    InvalidHandshake,
    WebSocketCommonProtocol,
    handshake,
)

class CustomProtocol(WebSocketProtocol):
    def __init__(
        self,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)



    async def websocket_handshake(self, request, subprotocols=None):
        # let the websockets package do the handshake with the client
        headers = {}

        try:
            print(request.headers)
            key = handshake.check_request(request.headers)
            handshake.build_response(headers, key)
        except InvalidHandshake:
            raise InvalidUsage("Invalid websocket request")

        subprotocol = None
        if subprotocols and "Sec-Websocket-Protocol" in request.headers:
            # select a subprotocol
            client_subprotocols = [
                p.strip()
                for p in request.headers["Sec-Websocket-Protocol"].split(",")
            ]
            for p in client_subprotocols:
                if p in subprotocols:
                    subprotocol = p
                    headers["Sec-Websocket-Protocol"] = subprotocol
                    break

        # write the 101 response back to the client
        rv = b"HTTP/1.1 101 Switching Protocols\r\n"
        for k, v in headers.items():
            rv += k.encode("utf-8") + b": " + v.encode("utf-8") + b"\r\n"
        rv += b"\r\n"
        request.transport.write(rv)

        # hook up the websocket protocol
        self.websocket = WebSocketCommonProtocol(
            timeout=self.websocket_timeout,
            max_size=self.websocket_max_size,
            max_queue=self.websocket_max_queue,
            read_limit=self.websocket_read_limit,
            write_limit=self.websocket_write_limit,
            ping_timeout=None,
        )
        # Following two lines are required for websockets 8.x
        self.websocket.is_client = False
        self.websocket.side = "server"
        self.websocket.subprotocol = subprotocol
        self.websocket.connection_made(request.transport)
        self.websocket.connection_open()
        return self.websocket