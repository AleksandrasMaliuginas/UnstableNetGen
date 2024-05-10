import re
import time
import logging
import subprocess
from enum import Enum
from utils.agent import Agent
from network.udp import UDPClient
from measurements import AppCounters
from messaging import Message, MessageType, Ping

log = logging.getLogger()


class ConnectionQuality:
    def __init__(self):
        self.reset()

    def reset(self):
        self.requestPacketCount = 0
        self.replyPacketCount = 0
        self.bytesTransferred = 0
        self.totalRoundTripTime = 0

    def packetDropPercentage(self) -> float:
        return round(100 * (1 - self.replyPacketCount / self.requestPacketCount), 2)

    def dataTransferRateBytesPerSecond(self) -> float:
        return round(self.bytesTransferred / self.totalRoundTripTime, 2)
    
    def dataTransferRateMBps(self) -> float:
        return round(self.bytesTransferred / self.totalRoundTripTime / 1_000_000, 2)

    def roundTripTimeSec(self) -> float:
        return self.totalRoundTripTime

    def __str__(self):
        return (
            f"{self.__class__.__name__}: "
            + f"requestPacketCount={self.requestPacketCount}; "
            + f"replyPacketCount={self.replyPacketCount}; "
            + f"bytesReceived={self.bytesTransferred}; "
            + f"totalRoundTripTime={self.totalRoundTripTime}; "
            + f"packetDropPercentage={self.packetDropPercentage()}; "
            + f"dataTransferRateBytesPerSecond={self.dataTransferRateBytesPerSecond()}; "
            + f"roundTripTimeSec={self.roundTripTimeSec()}; "
        )


class ConnectionObserver(Agent):

    IP_HEADER_LENGTH_BYTES = 12
    UDP_HEADER_LENGTH_BYTES = 8

    PING_MESSAGE_SIZE_BYTES = 64

    def __init__(self, client: UDPClient, measurePeriodSec: int):

        self.client = client
        self.measurePeriodSec = measurePeriodSec
        self.lastMeasurement = -1
        self.pingRepetitions = 100

        self.connectionQuality = None
        self.records = {}

    def doWork(self):

        self.measureRSSI()

        # if self.isTimeToMeasure():
        #     self.measureConnectionQuality()
        #     self.lastMeasurement = time.time()

        #     appCounters.report(Counters.PacketDropPercentage, self.connectionQuality.packetDropPercentage())
        #     appCounters.report(
        #         Counters.DataTransferRateBytesPerSecond, self.connectionQuality.dataTransferRateBytesPerSecond()
        #     )
        #     # log.info(appCounters)
        #     log.info(self.connectionQuality)

    def measureRSSI(self):
        process = subprocess.Popen("iwconfig", stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        for line in process.stdout.readlines():
            regex_signalStrength = re.compile(r"Signal level=(-\d+) dBm")
            regex_linkQuality = re.compile(r"Link Quality=(\d+\/\d+)")

            searchResult = regex_signalStrength.search(str(line))
            if searchResult:
                self.signalLevel = int(searchResult.groups()[0])

            searchResult = regex_linkQuality.search(str(line))
            if searchResult:
                self.linkQuality = searchResult.groups()[0]

        returnValue = process.wait()

    #
    #
    #

    # def isTimeToMeasure(self) -> bool:
    #     return time.time() > self.lastMeasurement + self.measurePeriodSec

    # def awaitInitialMeasurements(self, timeoutSec: int = 10):
    #     start = time.time()
    #     endAwaitTime = start + timeoutSec

    #     while self.connectionQuality == None and time.time() <= endAwaitTime:
    #         time.sleep(0.5)

    # TODO: Not thread safe
    def getConnectionQuality(self) -> ConnectionQuality:
        self.measureConnectionQuality()
        return self.connectionQuality

    def measureConnectionQuality(self):
        self.records.clear()

        st = time.time()
        for i in range(1, 1 + self.pingRepetitions):
            self.sendPing(i)
            self.awaitPingResponse()
        print("TIME:", time.time() - st)

        # TODO: Not thread safe
        connQuality = ConnectionQuality()
        self.aggregateResults(self.pingRepetitions, connQuality)
        self.connectionQuality = connQuality

    def aggregateResults(self, requestPacketCount: int, connQuality: ConnectionQuality):
        connQuality.reset()
        connQuality.requestPacketCount = requestPacketCount

        for seq, pingRecord in self.records.items():
            request, start, pingReqLength, end, pingReplyLength = pingRecord

            if end:
                connQuality.replyPacketCount += 1
                connQuality.bytesTransferred += self.PING_MESSAGE_SIZE_BYTES * 2
                connQuality.totalRoundTripTime += end - start
        
        # print("Speed:", round( / 1_000_000, 3))
        print(connQuality.bytesTransferred, connQuality.totalRoundTripTime)
        print(" Speed:", round(connQuality.bytesTransferred / connQuality.totalRoundTripTime / 1_000_000, 3))

    # Sending PING
    def sendPing(self, seq: int = 0):
        pingMessage = Ping(seq)
        pingEncoded = pingMessage.encode()

        start = time.time()
        self.client.send(pingEncoded)

        self.records[seq] = (pingMessage, start, len(pingEncoded), None, None)

    # Receiving PING
    def awaitPingResponse(self):
        self.client.awaitResponse(self.onPingResponse)

    def onPingResponse(self, message):
        # print("On resp message: ", len(message))
        end = time.time()
        if len(message) != self.PING_MESSAGE_SIZE_BYTES:
            return

        pingReply = Message.decode(message)

        if pingReply.msgType != MessageType.PING or pingReply.type != Ping.REPLY:
            return

        if pingReply.seq in self.records:
            request, start, pingReqLength, _, _ = self.records[pingReply.seq]
            self.records[pingReply.seq] = (request, start, pingReqLength, end, len(message))
            # print((request, start, pingReqLength, end, len(message)))

        # print(f"{len(message)} bytes: ping_seq={pingReply.seq} time={roundTripDurationMs} ms")
