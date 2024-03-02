import time
from typing import Callable
from network import Client, SendBoundary, ThroughputController

MAX_RATE_BYTES = 12_500_000_000  # 100Gbit/s


class TimeControlledOutput(ThroughputController, SendBoundary):

    def __init__(self, client: Client):
        self.client = client
        self.sendBarrier = SendBarrier()

        self.BUFFER_SIZE = 1024
        self.bytesPerSecond = MAX_RATE_BYTES

    def dataRate(self, bytesPerSecond: int):
        self.bytesPerSecond = bytesPerSecond

    def send(self, data: bytes) -> None:
        self.sendBarrier.reset(self.bytesPerSecond)

        self.client.send(data)
        # self.client.send(data, self)

    def passOver(self, data: bytes, offset: int, next: Callable[[bytes], int]):
        endPosition = min(offset + self.BUFFER_SIZE, len(data))

        self.sendBarrier.awaitSend()

        result = next(data[offset:endPosition])

        self.sendBarrier.report(result)

        return result


class SendBarrier:

    def __init__(self):
        self.reset()

    def reset(self, bytesPerSecond: int = MAX_RATE_BYTES):
        self.prevTime = None
        self.bytesAheadOfSchedule = 0
        self.maxSendRateBytesPerSecond = bytesPerSecond

    def awaitSend(self):
        if self.bytesAheadOfSchedule > 0:
            time.sleep(self.bytesToSeconds(self.bytesAheadOfSchedule))

        now = time.time()
        if self.prevTime != None:
            self.bytesAheadOfSchedule -= self.secondsToBytes(now - self.prevTime)
        self.prevTime = now

    def report(self, numBytesSent: int):
        if numBytesSent > 0:
            self.bytesAheadOfSchedule += numBytesSent

    def bytesToSeconds(self, numBytes):
        return float(numBytes) / self.maxSendRateBytesPerSecond

    def secondsToBytes(self, seconds):
        return seconds * self.maxSendRateBytesPerSecond
