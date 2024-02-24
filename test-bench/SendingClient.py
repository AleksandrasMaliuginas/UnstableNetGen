from network import Client
from imageUtils import imageToBytes


class SendingClient:

    def __init__(self, client: Client, server_ip: str, server_port: int) -> None:
        self.client = client
        self.server_ip = server_ip
        self.server_port = server_port

    def start(self) -> None:
        self.client.connect(self.server_ip, self.server_port)

        self.doWork()

    def doWork(self):
        # Any sort of behavior of Sending Client
        self.send_image()

    def send_image(self) -> None:
        bytesToSend = imageToBytes(0)
        self.client.send(bytesToSend)
