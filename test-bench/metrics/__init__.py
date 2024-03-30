import time
from network.udp import UDPClient
from messaging import Message, Ping

class ConnectionQualityContext:
    def __init__(self, packetDropPercentage: float, dataTransferRateBytesPerSecond: float):
        self.packetDropPercentage = packetDropPercentage
        self.dataTransferRateBytesPerSecond = dataTransferRateBytesPerSecond

class ConnectionObserver:

    def __init__(self, client: UDPClient):
        self.client = client
        self.pingMessagesSent = []

    def measure(self) -> ConnectionQualityContext:

        for i in range(1, 11):
            self.sendPing(i)


    def sendPing(self, seq: int = 0):
        pingRequest = Ping(seq).encode()

        start = time.time()
        self.client.send(pingRequest)


        self.client.awaitResponse(self.onPingResponse)

    
    def onPingResponse(message):
        end = time.time()
        roundTripDurationMs = int((end - start) * 1000)
        pingResponse = Message.decode(message)

        print(f"{len(message)} bytes: ping_seq={pingResponse.seq} time={roundTripDurationMs} ms")