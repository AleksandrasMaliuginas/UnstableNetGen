import time
import random
import socket
import socketserver
from typing import Callable
from struct import pack, unpack
from network import NANOSECOND, Server, Client


MAX_PACKET_SIZE = 32 * 1024

_requestHandler = None
""" The request handler for received message. Is instantiated on UDPServer creation. """
_messages = dict()
"""Received packets aggregates by messageId."""


class Message:
    """Received packets aggregate."""

    def __init__(self, length: int):
        self.length = length
        self.data = bytes()

    def append(self, data: bytes):
        self.data += data

    def fullyReceived(self) -> bool:
        return len(self.data) == self.length


def handleRequest(request: socket.socket, client_address, dataReceived: bytes):

    if _requestHandler is None:
        return

    response = _requestHandler(dataReceived)
    if response:
        request.sendto(response, client_address)


def handleDatagram(request: socket.socket, client_address, dataReceived: bytes, messageId: int, length: int):
    if not messageId in _messages:
        _messages[messageId] = Message(length)

    message: Message = _messages[messageId]
    message.append(dataReceived)

    if message.fullyReceived():
        handleRequest(request, client_address, message.data)
        del _messages[messageId]


class UDPHandler(socketserver.BaseRequestHandler):
    """
    The request handler for server.
    Is instantiated on every recv. Keeps no state.
    """

    def handle(self):
        data, request = self.request

        id, length = unpack(">xxLLxx", data[:12])

        handleDatagram(request, self.client_address, data[12:], id, length)


class UDPServer(Server):

    def __init__(self, host: str, port: int, requestHandler: Callable[[bytes], (None | bytes)]) -> None:
        global _requestHandler
        _requestHandler = requestHandler
        self.server = socketserver.UDPServer((host, port), UDPHandler)

    def listen(self):
        self.server.max_packet_size = MAX_PACKET_SIZE
        self.server.serve_forever(poll_interval=0.5)

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.server = None


class UDPClient(Client):

    def __init__(self, host: str, port: int, timeout: int = 1) -> None:
        self.address = (host, port)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)

    def send(self, data: bytes):

        messageId = random.randint(0, 4294967295)
        messageLength = len(data)

        while True:
            header = pack(">xxLLxx", messageId, messageLength)
            dataLength = min(len(data), MAX_PACKET_SIZE - len(header))

            self.socket.sendto(header + data[:dataLength], self.address)

            data = data[dataLength:]
            if len(data) == 0:
                break

            time.sleep(NANOSECOND)

    def awaitResponse(self, responseHandler: Callable[[bytes], None]) -> bool:
        try:
            response, address = self.socket.recvfrom(1024 * 1024)
            responseHandler(response)
            return True
        except socket.timeout:
            print("Request timed out.")
            return False

    def close(self):
        self.socket.close()
