from typing import Callable
from messaging import ImageFragment, ImageMetadata


class ImageReceiver:
    def __init__(self, imageHandler: Callable[[bytes], None]):
        self.imageHandler = imageHandler
        self.reset()

    def reset(self):
        self.bytesReceived = bytes()
        self.actingImageMetadata = None

    def onImageMetadata(self, imageMetadata: ImageMetadata):
        print(imageMetadata)
        self.actingImageMetadata = imageMetadata

    def onImageFragment(self, imageFragment: ImageFragment):

        if not self.actingImageMetadata:
            return

        self.bytesReceived += imageFragment.fragmentData

        if self.actingImageMetadata.imageLength == len(self.bytesReceived):
            self.imageHandler(self.bytesReceived)
