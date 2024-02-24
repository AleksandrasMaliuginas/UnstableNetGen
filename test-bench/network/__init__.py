class Client:

    def connect(self, server_ip: str, server_port: str):
        """Establish connection with a server."""
        pass

    def send(self, data: bytes):
        """Send image to a server."""
        pass

    def close(self):
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

    def send(self, data: bytes):
        """Propagate data further."""
        pass

    def set_throughput(self, bytes_per_second: int):
        """Set data flow rate."""
        pass
