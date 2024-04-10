import time
from typing import Callable
from threading import Thread
from network.udp import UDPServer

NANOSECOND = 1 / 1_000_000_000


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
        self.pollingDuty = Thread(name="POLLING_DUTY", target=self.pollInput)

        self.closed = False

    def run(self):
        self.server.start(self.server_ip, self.server_port)
        self.pollingDuty.start()

        self.server.listen()
        self.pollingDuty.join()

    def pollInput(self):
        while not self.closed:
            self.server.poll()
            time.sleep(NANOSECOND)

    def close(self):
        self.closed = True

        if self.server:
            self.server.close()
