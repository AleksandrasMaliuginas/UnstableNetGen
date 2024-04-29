import time
import logging
from enum import Enum
from pathlib import Path
from messaging import ImageFragment, ImageMetadata, ImageReceived, MessageType
from network.connection import ConnectionProvider
from infrastructure.sender.imageSend import ImageSender
from infrastructure.sender.dataset import Size, Dataset

# TODO: move to commons. Cannot depend on middle
from infrastructure.middle.messageRouter import MessageRouter
from measurements.connection import ConnectionObserver
from measurements import AppCounters
from utils.agent import AgentRunner

log = logging.getLogger()


class Counters(Enum):
    ImageId = 0
    ImageSizeBytes = 1
    CompressionDurationSec = 3
    CompressedImageSizeBytes = 4
    ImageSendingTime = 5


appCounters = AppCounters(Counters)


class SendingClient:

    def __init__(self, connectionProvider: ConnectionProvider):

        self.client = connectionProvider.getClient(timeoutSec=1)
        self.messageRouter = MessageRouter({MessageType.IMAGE_RECEIVED: self.onImageReceived})

        self.imageSender = ImageSender(self.client)

        self.connectionObserver = ConnectionObserver(self.client, measurePeriodSec=1)
        # self.metricsRunner = AgentRunner("METRICS_OBSERVER", periodicitySec=0.5, agent=self.connectionObserver)

    def start(self):
        # self.metricsRunner.start()

        self.datasetReader = Dataset(Path("../dataset").absolute())
        connectionQuality = self.connectionObserver.getConnectionQuality()

        repetitions = 10
        averageSpeed = 0
        for i in range(repetitions):
            averageSpeed += self.connectionObserver.getConnectionQuality().megaBits()
        
        print(f"Average: {round(averageSpeed/repetitions, 2)} Mbps")

        # self.close()
        # return

        self.stats()
        self.datasetReader.readAll(Size.HD_1k, self.sendImage)
        print(
            f"{self.imagesReceived} / {self.imagesSent} in "
            + f"{round(self.totalTimeAcc / self.imagesReceived, 5)} "
            + f"({round(self.sendingTimeAcc / self.imagesSent, 5)}) "
        )
        print(self.imageSizes)
        print(self.transferTimes)
        print(self.connectionSpeed)
        self.stats()
        self.datasetReader.readAll(Size.HD_2k, self.sendImage)
        print(
            f"{self.imagesReceived} / {self.imagesSent} in "
            + f"{round(self.totalTimeAcc / self.imagesReceived, 5)} "
            + f"({round(self.sendingTimeAcc / self.imagesSent, 5)}) "
        )
        print(self.imageSizes)
        print(self.transferTimes)
        print(self.connectionSpeed)
        self.stats()
        self.datasetReader.readAll(Size.HD_4k, self.sendImage)
        print(
            f"{self.imagesReceived} / {self.imagesSent} in "
            + f"{round(self.totalTimeAcc / self.imagesReceived, 5)} "
            + f"({round(self.sendingTimeAcc / self.imagesSent, 5)}) "
        )
        print(self.imageSizes)
        print(self.transferTimes)
        print(self.connectionSpeed)
        self.stats()
        self.datasetReader.readAll(Size.HD_8k, self.sendImage)
        print(
            f"{self.imagesReceived} / {self.imagesSent} in "
            + f"{round(self.totalTimeAcc / self.imagesReceived, 5)} "
            + f"({round(self.sendingTimeAcc / self.imagesSent, 5)}) "
        )
        print(self.imageSizes)
        print(self.transferTimes)
        print(self.connectionSpeed)

        self.close()

    def stats(self):
        self.imagesSent = 0
        self.imagesReceived = 0

        self.sendingTimeAcc = 0
        self.totalTimeAcc = 0

        self.imageSizes = []
        self.transferTimes = []
        self.connectionSpeed = []

    def sendImage(self, imageBytes: bytes):
        
        self.imageSendStart = time.time()
        self.imageSendSize = len(imageBytes)

        metadata = ImageMetadata(imageLength=len(imageBytes), fragmentLength=len(imageBytes))
        imageFragment = ImageFragment(sequenceNo=0, fragmentLength=len(imageBytes), fragmentData=imageBytes)

        self.client.send(metadata.encode())
        self.client.send(imageFragment.encode())

        self.imagesSent += 1
        self.sendingTimeAcc += time.time() - self.imageSendStart


        # Await image received
        repeat = 3
        imageReceived = False

        while not imageReceived:

            if repeat <= 0:
                break

            repeat -= 1
            imageReceived = self.client.awaitResponse(self.messageRouter.onPacketReceived)
            
        time.sleep(0.5)

    def onImageReceived(self, receivedImage: ImageReceived):
        # print(receivedImage)
        self.imagesReceived += 1
        sendDuration = time.time() - self.imageSendStart
        self.totalTimeAcc += sendDuration

        transferSpeed = round(self.imageSendSize / sendDuration * 8 / 1_000_000, 2)
        # print("Adjusted*: ", round(self.imageSendSize / sendDuration * 8 / 1_000_000, 2), "Mbps")

        self.imageSizes.append(self.imageSendSize)
        self.transferTimes = sendDuration
        self.connectionSpeed.append(transferSpeed)
        pass

    def shutdownBarrier(self):
        # if self.metricsRunner:
        #     try:
        #         self.metricsRunner.join()
        #     finally:
        #         self.close()
        pass

    def close(self):
        # if self.metricsRunner:
        #     self.metricsRunner.close()

        if self.client:
            self.client.close()
