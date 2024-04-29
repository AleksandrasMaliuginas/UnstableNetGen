import time
from typing import Callable
from messaging import ImageFragment, ImageMetadata


class ImageReceiver:
    def __init__(self, imageHandler: Callable[[bytes], None]):
        self.imageHandler = imageHandler
        
        self.bytesReceived = bytes()
        self.actingImageMetadata = None
        self.start = time.time()
        self.end = None

    def reset(self):
        self.bytesReceived = bytes()
        self.actingImageMetadata = None

        # if not self.end:
        #     print("Image was not received.")
        # else:
        #     print(self.end - self.start)

        self.start = time.time()
        self.end = None

    def onImageMetadata(self, imageMetadata: ImageMetadata):
        self.reset()
        self.actingImageMetadata = imageMetadata

    def onImageFragment(self, imageFragment: ImageFragment):

        if not self.actingImageMetadata:
            return

        self.bytesReceived += imageFragment.fragmentData

        if self.actingImageMetadata.imageLength == len(self.bytesReceived):
            return self.imageHandler(self.bytesReceived)
            # self.end = time.time()
            
