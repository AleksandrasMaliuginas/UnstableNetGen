import time
import logging
from enum import Enum
from pathlib import Path
from messaging import ImageFragment, ImageMetadata, ImageReceived, MessageType
from network.connection import ConnectionProvider
from infrastructure.sender.imageSend import ImageSender
from infrastructure.sender.dataset import CompressionLevel, DatasetImage, Resolution, Dataset

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

        self.client = connectionProvider.getClient(timeoutSec=10)
        self.messageRouter = MessageRouter({MessageType.IMAGE_RECEIVED: self.onImageReceived})

        self.imageSender = ImageSender(self.client)

        self.connectionObserver = ConnectionObserver(self.client, measurePeriodSec=1)
        # self.metricsRunner = AgentRunner("METRICS_OBSERVER", periodicitySec=0.5, agent=self.connectionObserver)

        self.dataset = Dataset(Path("../dataset/external").absolute())

    def start(self):
        self.connectionObserver.measureRSSI()

        # print(f"RSSI; LinkQuality; Bytes transferred; RTT; Derived speed MBps")  # throughput; latency
        # for i in range(10):
        #     connectionQuality = self.connectionObserver.getConnectionQuality()
        #     print(
        #         f"{self.connectionObserver.signalLevel}; {self.connectionObserver.linkQuality}; {connectionQuality.bytesTransferred}; {connectionQuality.roundTripTimeSec()}; {connectionQuality.dataTransferRateMBps()}"
        #     )

        self.imagesReceived = 0
        compressionLevel = CompressionLevel.NONE

        for res in Resolution:
            # print(res)
            self.dataset.readAll(self.sendImage, resolution=res, compression=compressionLevel)
        

        self.close()

    def sendImage(self, datasetImage: DatasetImage):

        fragments = datasetImage.imageTiles
        metadata = ImageMetadata(imageLength=datasetImage.totalImageSize, fragmentCount=len(fragments))
        metadataEncoded = metadata.encode()

        self.connectionObserver.measureRSSI()

        #             Image name           ; Compression Level            ; Total image in bytes;
        self.stats = [datasetImage.filename, datasetImage.compression.name, datasetImage.totalImageSize]
        #              Sygnal level dBm                   ; Link quality from iwconfig (x/70)
        self.stats += [self.connectionObserver.signalLevel, self.connectionObserver.linkQuality]

        self.sendStart = time.time()
        self.imageBytesSent = 0
        self.bytesTransferred = len(metadataEncoded)

        self.client.send(metadataEncoded)

        # Send images fragments (or aka tiles)
        seqNo = 0
        for imageFragment in fragments:
            fragmentName, fragmentBytes = imageFragment
            fragment = ImageFragment(sequenceNo=seqNo, fragmentLength=len(fragmentBytes), fragmentData=fragmentBytes)
            fragmentEncoded = fragment.encode()
            seqNo += 1

            self.client.send(fragmentEncoded)

            self.imageBytesSent += len(fragmentBytes)
            self.bytesTransferred += len(fragmentEncoded)

        if self.imageBytesSent != datasetImage.totalImageSize:
            print("ERROR: bytes sent does not match.")

        # Await image received
        repeat = 3
        imageReceived = False

        while not imageReceived:

            if repeat <= 0:
                break

            repeat -= 1
            imageReceived = self.client.awaitResponse(self.messageRouter.onPacketReceived)

        if not imageReceived:
            pass

        time.sleep(1)

        print("; ".join([str(val) for val in self.stats]))

    def onImageReceived(self, imageReceived: ImageReceived):

        self.imagesReceived += 1
        sendDuration = time.time() - self.sendStart
        transferRateBps = self.bytesTransferred / sendDuration

        #              Bytes transferred    ; Transfer time ; Derived link speed MBps
        self.stats += [self.bytesTransferred, sendDuration, round(transferRateBps / 1_000_000, 5)]

    def shutdownBarrier(self):
        if self.metricsRunner:
            try:
                self.metricsRunner.join()
            finally:
                self.close()
        pass

    def close(self):
        if self.metricsRunner:
            self.metricsRunner.close()

        if self.client:
            self.client.close()
