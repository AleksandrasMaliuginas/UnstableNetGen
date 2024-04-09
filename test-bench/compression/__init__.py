from measurements.connection import ConnectionQuality

class Encoder:

    def encode(self, image: bytes, connectionQuality: ConnectionQuality):
        """GenAI encoder."""
        raise Exception("Not implemented.")


class NoopEncoder(Encoder):
    def encode(self, image: bytes, connection_quality_context):
        # Do nothing
        return image
