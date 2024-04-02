from PIL import Image
from infrastructure.middle.receiver import ImageReceiver
from infrastructure.middle.receiverDuty import ReceiverDuty
from messaging import MessageType, Ping
from network.artificialControl import PacketController
from infrastructure.middle.messageRouter import MessageRouter
from utils.image import bytesToImage


class AccessPoint:

    def __init__(self, server_ip: str, server_port: int):
        self.imageReceiver = ImageReceiver(self.onImageReceived)

        messageRouter = MessageRouter(self.messageRoutes())
        packetController = PacketController(messageRouter.onPacketReceived)
        self.receiverDuty = ReceiverDuty("IMAGE_RECEIVER", server_ip, server_port, packetController.onPacketReceived)

    def start(self):
        self.receiverDuty.start()

    def onImageReceived(self, imageBytes: bytes):
        img: Image = bytesToImage(imageBytes)
        img.show("Received image")

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
        if self.receiverDuty:
            try:
                self.receiverDuty.join()
            finally:
                self.close()

    def close(self):
        if self.receiverDuty:
            self.receiverDuty.close()
