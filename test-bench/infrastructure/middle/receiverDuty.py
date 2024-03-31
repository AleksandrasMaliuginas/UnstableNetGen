from network.udp import UDPServer
from threading import Thread
from typing import Callable


class ReceiverDuty(Thread):
    def __init__(
        self,
        dutyName: str,
        server_ip: str,
        server_port: int,
        messageHandler: Callable[[bytes], (None | bytes)],
    ):
        Thread.__init__(self, name=dutyName)

        self.server_ip = server_ip
        self.server_port = server_port
        self.server = UDPServer(messageHandler)

    def run(self):
        self.server.start(self.server_ip, self.server_port)
        self.server.listen()

    def close(self):
        if self.server:
            self.server.close()
