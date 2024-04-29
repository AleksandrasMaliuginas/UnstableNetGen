from enum import Enum
from struct import pack, unpack


class MessageType(Enum):
    INVALID = -1
    PING = 0
    IMAGE_METADATA = 1
    IMAGE_RECEIVED = 2
    IMAGE_FRAGMENT = 3


class Message:

    def __init__(self, msgType: MessageType | int):
        if isinstance(msgType, MessageType):
            self.msgType = msgType
            self.msgTypeId = msgType.value
        else:
            self.msgType = MessageType.INVALID
            self.msgTypeId = msgType

    def __str__(self):
        return (
            f"Message msgTypeId={self.msgTypeId}"
            if self.msgType == MessageType.INVALID
            else f"Message msgType={self.msgType.name}"
        )

    def encode(self):
        return pack(">H", self.msgTypeId)

    @staticmethod
    def decode(buffer: bytes):

        msgTypeId: int = unpack(">H", buffer[:2])[0]

        if msgTypeId == MessageType.PING.value:
            return Ping.decode(buffer=buffer[2:])

        if msgTypeId == MessageType.IMAGE_METADATA.value:
            return ImageMetadata.decode(buffer=buffer[2:])

        if msgTypeId == MessageType.IMAGE_FRAGMENT.value:
            return ImageFragment.decode(buffer=buffer[2:])
        
        if msgTypeId == MessageType.IMAGE_RECEIVED.value:
            return ImageReceived.decode(buffer=buffer[2:])

        return Message(msgTypeId)


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

class ImageReceived(Message):

    def __init__(self):
        super().__init__(MessageType.IMAGE_RECEIVED)
        # self.imageLength = imageLength
        # self.fragmentLength = fragmentLength
        # requestId, imageSize, encoderId, imageId ?

    def __str__(self):
        return super().__str__() + f" Wooooooow "

    def encode(self):
        return super().encode() #+ pack(">x")

    @staticmethod
    def decode(buffer: bytes):
        # imageLength, fragmentLength = unpack(">LL", buffer)

        return ImageReceived()

class Ping(Message):

    REPLY = 0
    REQUEST = 1

    padding_bytes = 4 + 3 * 16

    def __init__(self, seq: int, isReply: bool = False):
        super().__init__(MessageType.PING)
        self.type = Ping.REPLY if isReply else Ping.REQUEST
        self.seq = seq

    def __str__(self):
        return super().__str__() + f" {self.type} seq={self.seq}"

    def encode(self):
        return super().encode() + pack(">HQ", self.type, self.seq) + bytes(Ping.padding_bytes)

    @staticmethod
    def decode(buffer: bytes):
        type, seq = unpack(f">HQ{Ping.padding_bytes}x", buffer)

        if type == Ping.REPLY:
            return Ping(seq, True)
        else:
            return Ping(seq, False)
