from network.udp import UDPClient
from messaging import ImageFragment, ImageMetadata


class ImageSender:
    def __init__(self, client: UDPClient):
        self.client = client

        self.fragmentSize = 8 * 1024

    def sendImage(self, imageBytes: bytes) -> None:

        # Send image metadata
        metadata = self.imageMetadata(imageBytes)
        print("Image metadata:", metadata)
        self.client.send(metadata.encode())

        # Send fragmented image
        self.sendImageFragments(imageMetadata=metadata, imageBytes=imageBytes)

    def imageMetadata(self, imageBytes: bytes):
        return ImageMetadata(imageLength=len(imageBytes), fragmentCount=self.fragmentSize)

    def sendImageFragments(self, imageMetadata: ImageMetadata, imageBytes: bytes):
        totalLength = imageMetadata.imageLength
        fragmentLength = imageMetadata.fragmentCount

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
