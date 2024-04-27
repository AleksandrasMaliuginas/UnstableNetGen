from enum import Enum
from typing import Callable
from network import Client, Server
from network.tcp import TCPClient, TCPServer
from network.udp import UDPClient, UDPServer


class Protocol(Enum):
    """Supported protocols."""

    TCP = "TCP"
    UDP = "UDP"
    # TODO: RUDP = "Reliable UDP"
    # TODO: IP = "IP"


class ConnectionProvider:

    def __init__(self, host: str, port: int, protocol: Protocol):
        self.host_ip = host
        self.port = port
        self.protocol = protocol

    def getServer(self, requestHandler: Callable[[bytes], (None | bytes)]) -> Server:

        if self.protocol == Protocol.TCP:
            return TCPServer(self.host_ip, self.port, requestHandler)

        if self.protocol == Protocol.UDP:
            return UDPServer(self.host_ip, self.port, requestHandler)

        raise f"Unknown protocol {self.protocol}."

    def getClient(self, timeoutSec: int) -> Client:

        if self.protocol == Protocol.TCP:
            return TCPClient(self.host_ip, self.port, timeoutSec)

        if self.protocol == Protocol.UDP:
            return UDPClient(self.host_ip, self.port, timeoutSec)

        raise f"Unknown protocol {self.protocol}."
