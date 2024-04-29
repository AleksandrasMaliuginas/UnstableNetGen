import time
import random
from typing import Callable


class PacketDropStrategy:
    def dropPacket() -> bool:
        return False


class RandomPacketDrop(PacketDropStrategy):

    def __init__(self, dropPercentage: float = 50.0) -> None:
        self.dropThreshold = dropPercentage / 100

    def dropPacket(self) -> bool:
        return random.random() < self.dropThreshold


class PacketController:

    MAX_BYTES_PER_SECOND = 1024 * 1024 * 1024 * 1024
    UNLIMITED = -1

    def __init__(
        self,
        messageHandler: Callable[[bytes], (None | bytes)],
        receivingRate: int = UNLIMITED,
        packetDropStrategy: PacketDropStrategy = PacketDropStrategy,
    ):
        self.messageHandler = messageHandler

        self.desiredBytesPerSecond = receivingRate
        self.packetDropStrategy = packetDropStrategy

    def onPacketReceived(self, data: bytes) -> bytes:

        self.throughputAwait(bytesReceived=len(data))

        if self.packetDropStrategy.dropPacket():
            return None

        return self.messageHandler(data)

    def throughputAwait(self, bytesReceived: int):
        if self.desiredBytesPerSecond != -1:
            time.sleep(float(bytesReceived) / self.desiredBytesPerSecond)
