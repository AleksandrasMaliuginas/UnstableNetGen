from PIL import Image
from Receiver import ImageReceiver, ReceiverDuty
from messaging import Message, MessageType
from imageUtils import bytesToImage


class AccessPoint:

    def __init__(self, server_ip: str, server_port: int):
        self.receiverDuty = ReceiverDuty("IMAGE_RECEIVER", server_ip, server_port, self.onIncomingMessage)
        self.receiver = ImageReceiver(self.onImageReceived)

    def start(self):
        self.receiverDuty.start()

    def onImageReceived(self, imageBytes: bytes):
        img: Image = bytesToImage(imageBytes)
        img.show("Received image")

    def onIncomingMessage(self, messageBuffer: bytes) -> bytes:

        message = Message.decode(messageBuffer)

        if message.msgType == MessageType.IMAGE_METADATA:
            self.receiver.onImageMetadata(message)

        elif message.msgType == MessageType.IMAGE_FRAGMENT:
            self.receiver.onImageFragment(message)

        return b"Message handled"

    def shutdownBarrier(self):
        if self.receiverDuty:
            try:
                self.receiverDuty.join()
            finally:
                self.close()

    def close(self):
        if self.receiverDuty:
            self.receiverDuty.close()
