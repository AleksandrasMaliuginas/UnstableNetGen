import time
import socket
import socketserver
from typing import Callable
from struct import pack, unpack
from network import NANOSECOND, Client, Server

_requestHandler = None
""" The request handler for received message.
    Is instantiated on TCPServer creation. """


def handleRequest(socket: socket.socket, dataReceived: bytes):

    if _requestHandler is None:
        return

    response = _requestHandler(dataReceived)
    if response:
        socket.sendall(response)


class TCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler for server.
    Is instantiated once per connection to the server.
    """

    def setup(self):
        self.receivedData = bytes()
        self.remainingBytes = 0

    def handle(self):
        self.socket: socket.socket = self.request

        while True:
            if self.remainingBytes == 0:
                header = self.socket.recv(8)

                if len(header) == 0:
                    return

                requestLength = unpack(">xxLxx", header)[0]

                self.remainingBytes = requestLength
                self.receivedData = bytes()

            data = self.socket.recv(min(1024 * 1024, self.remainingBytes))

            self.receivedData += data
            self.remainingBytes -= len(data)

            if self.remainingBytes == 0:
                handleRequest(self.socket, self.receivedData)

            time.sleep(NANOSECOND)


class TCPServer(Server):

    def __init__(self, host: str, port: int, requestHandler: Callable[[bytes], (None | bytes)]) -> None:
        global _requestHandler
        _requestHandler = requestHandler
        self.server = socketserver.TCPServer((host, port), TCPHandler)

    def listen(self):
        self.server.serve_forever(poll_interval=0.5)

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.server = None


class TCPClient(Client):

    def __init__(self, host: str, port: int, timeout: int = 1) -> None:
        self.address = (host, port)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(timeout)

        self.connected = False

    def send(self, data: bytes):
        if not self.connected:
            self.socket.connect(self.address)
            self.connected = True

        header = pack(">xxLxx", len(data))
        self.socket.sendall(header + data)

    def awaitResponse(self, responseHandler: Callable[[bytes], None]) -> bool:
        try:
            response, address = self.socket.recvfrom(1024 * 1024)
            responseHandler(response)
            return True
        except socket.timeout:
            print("Request timed out.")
            return False

    def close(self):
        self.socket.shutdown(socket.SHUT_WR)
        self.connected = False
        self.socket.close()
