from imageUtils import imageToBytes
from compression import Encoder
from network.udp import UDPClient
from messaging import ImageFragment, ImageMetadata


class SendingClient:

    def __init__(self, server_ip: str, server_port: int, encoder: Encoder):

        self.client = UDPClient(server_ip, server_port, timeoutSeconds=4)
        self.server_ip = server_ip
        self.server_port = server_port

        self.encoder = encoder

        self.fragmentSize = 8 * 1024

    def start(self) -> None:
        self.doWork()

    def doWork(self):
        # Any sort of behavior of Sending Client
        self.send_image()

    def send_image(self) -> None:

        imageBytes = imageToBytes(0)
        encodedImageBytes = self.encoder.encode(imageBytes, None)

        # Send image metadata
        metadata = self.imageMetadata(encodedImageBytes)
        print("Send: ", metadata)
        self.client.send(metadata.encode())

        # Send fragmented image
        self.sendImageFragments(imageMetadata=metadata, imageBytes=encodedImageBytes)

    def imageMetadata(self, imageBytes: bytes):
        return ImageMetadata(imageLength=len(imageBytes), fragmentLength=self.fragmentSize)

    def sendImageFragments(self, imageMetadata: ImageMetadata, imageBytes: bytes):
        totalLength = imageMetadata.imageLength
        fragmentLength = imageMetadata.fragmentLength

        offset = 0
        sequenceNo = 0

        while offset < totalLength:
            endPosition = min(offset + fragmentLength, totalLength)

            segmentBody = imageBytes[offset:endPosition]

            imageFragment = ImageFragment(
                sequenceNo=sequenceNo, fragmentLength=len(segmentBody), fragmentData=segmentBody
            )

            # print("Send: ", imageFragment)
            self.client.send(imageFragment.encode())

            offset += fragmentLength
            sequenceNo += 1
