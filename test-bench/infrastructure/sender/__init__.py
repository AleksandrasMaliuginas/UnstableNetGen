from compression import Encoder
from network.udp import UDPClient
from measurements import ConnectionObserver
from utils.agent import AgentRunner
from infrastructure.sender.imageSend import ImageSender
from utils.image import imageToBytes


class SendingClient:

    def __init__(self, server_ip: str, server_port: int, encoder: Encoder):

        self.client = UDPClient(server_ip, server_port, timeoutSeconds=4)

        self.imageSender = ImageSender(self.client)

        self.encoder = encoder

        self.connectionObserver = ConnectionObserver(self.client, measurePeriodSec=2)
        self.metricsRunner = AgentRunner("METRICS_OBSERVER", periodicitySec=0.5, agent=self.connectionObserver)

    def start(self) -> None:
        self.metricsRunner.start()
        self.doWork()

    def doWork(self):
        self.connectionObserver.awaitInitialMeasurements()

        self.sendImage(0)

        self.close()

    def sendImage(self, imageKey: int):
        imageBytes = imageToBytes(imageKey)

        connectionQuality = self.connectionObserver.getConnectionQuality()

        encodedImage = self.encoder.encode(imageBytes, connectionQuality)

        self.imageSender.sendImage(encodedImage)

    def shutdownBarrier(self):
        if self.metricsRunner:
            try:
                self.metricsRunner.join()
            finally:
                self.close()

    def close(self):
        if self.metricsRunner:
            self.metricsRunner.close()

        if self.client:
            self.client.close()
