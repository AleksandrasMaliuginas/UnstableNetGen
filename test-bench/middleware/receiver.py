from typing import Callable
from messaging import ImageFragment, ImageMetadata


class ImageReceiver:
    def __init__(self, imageHandler: Callable[[bytes], None]):
        self.imageHandler = imageHandler

        self.actingImageMetadata = None
        self.bytesReceived = bytes()

    def onImageMetadata(self, imageMetadata: ImageMetadata):
        print(imageMetadata)

        self.bytesReceived = bytes()
        self.actingImageMetadata = imageMetadata

    def onImageFragment(self, imageFragment: ImageFragment):
        print(imageFragment)

        self.bytesReceived += imageFragment.fragmentData

        if self.actingImageMetadata.imageLength == len(self.bytesReceived):
            self.imageHandler(self.bytesReceived)
