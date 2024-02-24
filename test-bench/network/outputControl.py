from network import Client, ThroughputController


class TimeControlledOutput(ThroughputController):

    def __init__(self, client: Client):
        self.client = client
        self.data_rate = 1

    def send(self, data: bytes) -> None:
        self.client.send(data)

    def set_throughput(self, bytes_per_second: int) -> None:
        self.data_rate = bytes_per_second
