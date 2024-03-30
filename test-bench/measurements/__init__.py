import time
from network.udp import UDPClient
from messaging import Message, MessageType, Ping
from utils.agent import Agent


class ConnectionQuality:
    def __init__(self):
        self.reset()

    def reset(self):
        self.requestPacketCount = 0
        self.replyPacketCount = 0
        self.bytesReceived = 0
        self.totalRoundTripTime = 0

    def packetDropPercentage(self) -> float:
        return round(100 * (1 - self.replyPacketCount / self.requestPacketCount), 2)

    def dataTransferRateBytesPerSecond(self) -> float:
        return round(self.bytesReceived / self.totalRoundTripTime, 2)

    def roundTripTimeMs(self, precision: int = 2) -> float:
        return round(1000 * self.totalRoundTripTime / self.replyPacketCount, precision)

    def __str__(self):
        return (
            f"{self.__class__.__name__}: "
            + f"requestPacketCount={self.requestPacketCount}; "
            + f"replyPacketCount={self.replyPacketCount}; "
            + f"bytesReceived={self.bytesReceived}; "
            + f"totalRoundTripTime={self.totalRoundTripTime}; "

            + f"packetDropPercentage={self.packetDropPercentage()}; "
            + f"dataTransferRateBytesPerSecond={self.dataTransferRateBytesPerSecond()}; "
            + f"roundTripTimeMs={self.roundTripTimeMs()}; "
        )


class ConnectionObserver(Agent):

    IP_HEADER_LENGTH_BYTES = 12
    UDP_HEADER_LENGTH_BYTES = 8

    PING_MESSAGE_SIZE_BYTES = 64

    def __init__(self, client: UDPClient):

        self.client = client
        self.pingPeriod = 0.5
        self.pingRepetitions = 10

        self.connectionQuality = None
        self.records = {}

    def doWork(self):
        self.measureConnectionQuality()
    
    def awaitInitialMeasurements(self, timeoutSec: int = 10):
        start = time.time()
        endAwaitTime = start + timeoutSec

        while self.connectionQuality == None and endAwaitTime <= time.time():
            time.sleep(0.5)

    # TODO: Not thread safe
    def getConnectionQuality(self) -> ConnectionQuality:
        return self.connectionQuality

    def measureConnectionQuality(self):
        self.records.clear()

        for i in range(1, 1 + self.pingRepetitions):
            self.sendPing(i)
            self.awaitPingResponse()

        # TODO: Not thread safe
        connQuality = ConnectionQuality()
        self.aggregateResults(self.pingRepetitions, connQuality)
        self.connectionQuality = connQuality

    def aggregateResults(self, requestPacketCount: int, connQuality: ConnectionQuality):
        connQuality.reset()
        connQuality.requestPacketCount = requestPacketCount

        for seq, pingRecord in self.records.items():
            request, start, end = pingRecord

            if end:
                connQuality.replyPacketCount += 1
                connQuality.bytesReceived += self.PING_MESSAGE_SIZE_BYTES
                connQuality.totalRoundTripTime += end - start

    # Sending PING
    def sendPing(self, seq: int = 0):
        pingMessage = Ping(seq)

        start = time.time()
        self.client.send(pingMessage.encode())

        self.records[seq] = (pingMessage, start, None)

    # Receiving PING
    def awaitPingResponse(self):
        self.client.awaitResponse(self.onPingResponse)

    def onPingResponse(self, message):
        end = time.time()
        pingReply = Message.decode(message)

        if pingReply.msgType != MessageType.PING or pingReply.type != Ping.REPLY:
            return

        request, start, _ = self.records[pingReply.seq]

        self.records[pingReply.seq] = (request, start, end)

        # print(f"{len(message)} bytes: ping_seq={pingReply.seq} time={roundTripDurationMs} ms")
