from PIL import Image
from threading import Thread
from messaging import MessageType, Ping, ImageReceived
from network.connection import ConnectionProvider
from network.artificialControl import PacketController
from infrastructure.middle.receiver import ImageReceiver
from infrastructure.middle.messageRouter import MessageRouter
from utils.image import bytesToImage


class AccessPoint:

    def __init__(self, connectionProvider: ConnectionProvider):
        self.imageReceiver = ImageReceiver(self.onImageReceived)

        messageRouter = MessageRouter(self.messageRoutes())
        packetController = PacketController(messageRouter.onPacketReceived)

        self.server = connectionProvider.getServer(packetController.onPacketReceived)
        self.receivingServer = Thread(name="SERVER_RECEIVE", target=self.server.listen)

    def start(self):
        self.receivingServer.start()
        self.imagesReceived = 0

    def onImageReceived(self, imageBytes: bytes):

        img: Image = bytesToImage(imageBytes)
        # img.show("Received image")
        self.imagesReceived += 1
        print("Image received ", self.imagesReceived, len(imageBytes))
        return ImageReceived().encode()

    def onPingMessage(self, pingMessage: Ping):
        pingReply = Ping(pingMessage.seq, isReply=True)
        return pingReply.encode()

    def messageRoutes(self) -> dict:
        return {
            MessageType.IMAGE_METADATA: self.imageReceiver.onImageMetadata,
            MessageType.IMAGE_FRAGMENT: self.imageReceiver.onImageFragment,
            MessageType.PING: self.onPingMessage,
        }

    def shutdownBarrier(self):
        if self.receivingServer:
            try:
                self.receivingServer.join()
            finally:
                self.close()

    def close(self):
        if self.server:
            self.server.close()
