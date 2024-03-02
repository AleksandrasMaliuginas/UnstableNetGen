from typing import Callable


class SendBoundary:
    NOOP = lambda data, offset, next: next(data[offset:])

    def passOver(self, data: bytes, offset: int, next: Callable[[bytes], int]) -> int:
        """Boundary to intercept sending data before each send request.
        Returns: bytes send."""
        return SendBoundary.NOOP(data, offset, next)


class Client:

    def connect(self, server_ip: str, server_port: str) -> None:
        """Establish connection with a server."""
        pass

    def send(self, data: bytes, sendBoundary: SendBoundary = SendBoundary()) -> None:
        """Send image to a server."""
        pass

    def close(self) -> None:
        """Close open socket."""
        pass


class Server:

    def start(self, server_ip: str, server_port: str):
        """Open port for incoming traffic."""
        pass

    def listen(self):
        """Start listening for connections."""
        pass

    def close(self):
        """Close open socket."""
        pass


class ThroughputController:

    def send(self, data: bytes) -> None:
        """Propagate data further."""
        pass

    def dataRate(self, bytesPerSecond: int) -> None:
        """Set data flow rate."""
        pass
