import time
import logging
from enum import Enum
from compression import Encoder
from network.udp import UDPClient
from measurements.connection import ConnectionObserver
from utils.agent import AgentRunner
from infrastructure.sender.imageSend import ImageSender
from utils.image import imageToBytes
from measurements import AppCounters

log = logging.getLogger()


class Counters(Enum):
    ImageId = 0
    ImageSizeBytes = 1
    CompressionDurationSec = 3
    CompressedImageSizeBytes = 4
    ImageSendingTime = 5


appCounters = AppCounters(Counters)


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

        imagesToSend = [1]
        for imageKey in imagesToSend:
            self.sendImage(imageKey)

        self.close()

    def sendImage(self, imageKey: int):

        imageBytes = imageToBytes(imageKey)

        appCounters.report(Counters.ImageId, imageKey)
        appCounters.report(Counters.ImageSizeBytes, len(imageBytes))

        connectionQuality = self.connectionObserver.getConnectionQuality()

        startCompression = time.time()
        encodedImage = self.encoder.encode(imageBytes, connectionQuality)

        appCounters.reportDuration(Counters.CompressionDurationSec, startCompression)
        appCounters.report(Counters.CompressedImageSizeBytes, len(encodedImage))

        startImageSend = time.time()
        self.imageSender.sendImage(encodedImage)

        appCounters.reportDuration(Counters.ImageSendingTime, startImageSend)
        log.info(appCounters)

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
