from typing import Callable
from abc import ABC, abstractmethod

NANOSECOND = 1 / 1_000_000_000


class Server(ABC):

    @abstractmethod
    def listen(self):
        """Blocking socket read. Can be interrupted by calling close() or by KeyboardInterrupt."""

    @abstractmethod
    def close(self):
        """Releases acquired server resources."""


class Client(ABC):

    @abstractmethod
    def send(self, data: bytes):
        """Blocking send bytes to socket."""

    @abstractmethod
    def awaitResponse(self, responseHandler: Callable[[bytes], None]) -> bool:
        """Blocking await for server response.
        Can be called from different thread.
        """

    @abstractmethod
    def close(self):
        """Releases acquired server resources."""
