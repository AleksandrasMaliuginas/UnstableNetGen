import socket
from struct import pack, unpack
from network import Client


class TCPClient(Client):

    def connect(self, server_ip: str, server_port: str):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server_ip, server_port))

    def close(self):
        self.socket.shutdown(socket.SHUT_WR)
        self.socket.close()
        self.socket = None

    def send(self, data: bytes):

        # use struct to make sure we have a consistent endianness on the length
        length = pack(">Q", len(data))

        # sendall to make sure it blocks if there's back-pressure on the socket
        self.socket.sendall(length)
        self.socket.sendall(data)

        ack = self.socket.recv(1)


class TCPServer:

    def __init__(self, requestHandler) -> None:
        self.requestHandler = requestHandler

    def start(self, server_ip, server_port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((server_ip, server_port))
        self.socket.listen(1)

    def listen(self):
        print('Listening...')
        try:
            while True:
                (connection, addr) = self.socket.accept()
                try:
                    bs = connection.recv(8)
                    (length,) = unpack(">Q", bs)
                    data = b""
                    while len(data) < length:
                        # doing it in batches is generally better than trying
                        # to do it all in one go, so I believe.
                        to_read = length - len(data)
                        data += connection.recv(4096 if to_read > 4096 else to_read)

                    # send our 0 ack
                    connection.sendall(b"\00")
                finally:
                    connection.shutdown(socket.SHUT_WR)
                    connection.close()

                self.requestHandler(data)

        finally:
            self.close()

    def close(self):
        self.socket.close()
        self.socket = None
