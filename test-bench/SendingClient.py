from network import Client, ThroughputController
from imageUtils import imageToBytes
from generativeAI import Encoder
from network.ControllerOutput import TimeControlledOutput


DATA_RATE = {
    "1 Gbit/s": 125_000_000,
    "100 Mbit/s": 12_500_000,
    "1 Mbit/s": 125_000,
}


class SendingClient:

    def __init__(
        self,
        client: Client,
        server_ip: str,
        server_port: int,
        encoder: Encoder,
    ):
        self.client = client
        self.server_ip = server_ip
        self.server_port = server_port

        self.output: ThroughputController = TimeControlledOutput(self.client)
        self.encoder = encoder

    def start(self) -> None:
        self.client.connect(self.server_ip, self.server_port)
        self.output.dataRate(DATA_RATE["1 Gbit/s"])

        self.doWork()

    def doWork(self):
        # Any sort of behavior of Sending Client
        self.send_image()

    def send_image(self) -> None:

        imageBytes = imageToBytes(0)
        encodedImageBytes = self.encoder.encode(imageBytes, None)

        self.output.send(encodedImageBytes)
