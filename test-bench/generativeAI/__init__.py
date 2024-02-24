class Encoder:

    def encode(self, image: bytes, connection_quality_context):
        """GenAI encoder."""
        raise Exception("Not implemented.")


class NoopEncoder(Encoder):
    def encode(self, image: bytes, connection_quality_context):
        # Do nothing
        return image
