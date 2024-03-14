import socket
from typing import Callable

BUFF_SIZE = 1024


class UDPServer:

    def __init__(
        self, server_hostname: str, port: int, requestHandler: Callable[[bytes], None]
    ):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.server_hostname = server_hostname
        self.port = port
        self.requestHandler = requestHandler
        self.closed = False

    def start(self):
        self.server_socket.bind((self.server_hostname, self.port))

    def listen(self):

        while not self.closed:
            message, address = self.server_socket.recvfrom(BUFF_SIZE)

            response = self.requestHandler(message)

            self.server_socket.sendto(response, address)

    def close(self):
        self.closed = True
        self.server_socket.close()
        self.server_socket = None


class UDPClient:

    def __init__(self, server_hostname: str, port: int, timeoutSeconds: float = 1.0):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.settimeout(timeoutSeconds)

        self.address = (server_hostname, port)

    def send(self, message):
        self.client_socket.sendto(message, self.address)

    def awaitResponse(self, responseHandler: Callable[[bytes], None]) -> bool:
        try:
            response, server = self.client_socket.recvfrom(1024)
            responseHandler(response)
            return True
        except socket.timeout:
            print("Request timed out.")
            return False
