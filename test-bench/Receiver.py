from typing import Callable
from threading import Thread
from network.udp import UDPServer
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


class ReceiverDuty(Thread):
    def __init__(self, dutyName: str, server_ip: str, server_port: int, messageHandler: Callable[[bytes], None]):
        Thread.__init__(self, name=dutyName)

        self.server_ip = server_ip
        self.server_port = server_port
        self.server = UDPServer(messageHandler)

    def run(self):
        self.server.start(self.server_ip, self.server_port)
        self.server.listen()

    def close(self):
        if self.server:
            self.server.close()
