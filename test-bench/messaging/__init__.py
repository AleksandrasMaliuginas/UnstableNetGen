from enum import Enum
from struct import pack, unpack


class MessageType(Enum):
    INVALID = -1
    PING = 0
    IMAGE_METADATA = 1
    IMAGE_FRAGMENT = 2


class Message:

    def __init__(self, msgType: MessageType):
        self.msgType = msgType

    def __str__(self):
        return f"Message msgType={self.msgType.name}"

    def encode(self):
        return pack(">H", self.msgType.value)

    @staticmethod
    def decode(buffer: bytes):

        msgTypeId = unpack(">H", buffer[:2])[0]
        decodedMessage = Message(MessageType.INVALID)

        if msgTypeId == MessageType.PING.value:
            pass

        elif msgTypeId == MessageType.IMAGE_METADATA.value:
            decodedMessage = ImageMetadata.decode(buffer=buffer[2:])

        elif msgTypeId == MessageType.IMAGE_FRAGMENT.value:
            decodedMessage = ImageFragment.decode(buffer=buffer[2:])

        return decodedMessage


class ImageMetadata(Message):

    def __init__(self, imageLength: int, fragmentLength: int):
        super().__init__(MessageType.IMAGE_METADATA)
        self.imageLength = imageLength
        self.fragmentLength = fragmentLength
        # requestId, imageSize, encoderId, imageId ?

    def __str__(self):
        return super().__str__() + f" imageLength={self.imageLength} fragmentLength={self.fragmentLength}"

    def encode(self):
        return super().encode() + pack(">LL", self.imageLength, self.fragmentLength)

    @staticmethod
    def decode(buffer: bytes):
        imageLength, fragmentLength = unpack(">LL", buffer)

        return ImageMetadata(imageLength, fragmentLength)


class ImageFragment(Message):

    def __init__(self, sequenceNo: int, fragmentLength: int, fragmentData: bytes):
        super().__init__(MessageType.IMAGE_FRAGMENT)
        self.sequenceNo = sequenceNo
        self.fragmentLength = fragmentLength
        self.fragmentData = fragmentData
        # requestId

    def __str__(self):
        return super().__str__() + f" sequenceNo={self.sequenceNo} fragmentLength={self.fragmentLength}"

    def encode(self):
        return super().encode() + pack(">LL", self.sequenceNo, self.fragmentLength) + self.fragmentData

    @staticmethod
    def decode(buffer: bytes):
        HEADER_SIZE = 8

        sequenceNo, fragmentLength = unpack(">LL", buffer[:HEADER_SIZE])

        return ImageFragment(sequenceNo, fragmentLength, buffer[HEADER_SIZE:])
