import socket
from typing import Callable

MAX_BUFF_SIZE = 1024 * 1024


class UDPServer:

    def __init__(self, requestHandler: Callable[[bytes], (None | bytes)]):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.messageHandler = requestHandler
        self.closed = False

    def start(self, server_hostname: str, port: int):
        self.server_socket.bind((server_hostname, port))
        print(f"UDP socket open on port {port}.")

    def listen(self):

        while not self.closed:
            message, address = self.server_socket.recvfrom(MAX_BUFF_SIZE)

            response = self.messageHandler(message)

            if response:
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

    def send(self, message: bytes):
        self.client_socket.sendto(message, self.address)

    def awaitResponse(self, responseHandler: Callable[[bytes], None]) -> bool:
        try:
            response, server = self.client_socket.recvfrom(MAX_BUFF_SIZE)
            responseHandler(response)
            return True
        except socket.timeout:
            print("Request timed out.")
            return False
