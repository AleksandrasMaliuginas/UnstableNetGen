from PIL import Image
from infrastructure.middle.receiver import ImageReceiver
from infrastructure.middle.receiverDuty import ReceiverDuty
from messaging import Message, MessageType, Ping
from network.artificialControl import PacketController, RandomPacketDrop
from utils.image import bytesToImage


class AccessPoint:

    def __init__(self, server_ip: str, server_port: int):
        packetController = PacketController(self.onIncomingMessage)

        self.receiverDuty = ReceiverDuty("IMAGE_RECEIVER", server_ip, server_port, packetController.onPacketReceived)
        self.imageReceiver = ImageReceiver(self.onImageReceived)

    def start(self):
        self.receiverDuty.start()

    def onImageReceived(self, imageBytes: bytes):
        img: Image = bytesToImage(imageBytes)
        img.show("Received image")

    def onPingMessage(self, pingMessage: Ping):
        pingReply = Ping(pingMessage.seq, isReply=True)
        return pingReply.encode()

    # Message router
    def onIncomingMessage(self, messageBuffer: bytes):

        message = Message.decode(messageBuffer)

        if message.msgType == MessageType.IMAGE_METADATA:
            return self.imageReceiver.onImageMetadata(message)

        elif message.msgType == MessageType.IMAGE_FRAGMENT:
            return self.imageReceiver.onImageFragment(message)

        elif message.msgType == MessageType.PING:
            return self.onPingMessage(message)

        print("Unrecognized message:", message)

    def shutdownBarrier(self):
        if self.receiverDuty:
            try:
                self.receiverDuty.join()
            finally:
                self.close()

    def close(self):
        if self.receiverDuty:
            self.receiverDuty.close()
