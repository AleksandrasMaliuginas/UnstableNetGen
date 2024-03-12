from PIL import Image
from imageUtils import bytesToImage
from threading import Thread
from network.tcp import TCPServer

class AccessPoint:

    def __init__(self, server_ip: str, server_port: int):
        self.receiver = Receiver(server_ip, server_port)
        # self.sender =

    def start(self):
        self.receiver.start()
        # self.sender.start()

    def shutdownBarrier(self):
        if self.receiver:
            try:
                self.receiver.join()
            finally:
                self.close()
    
    def close(self):
        if self.receiver:
            self.receiver.close()


class Receiver(Thread):
    def __init__(self, server_ip: str, server_port: int):
        Thread.__init__(self, name="IMAGE_RECEIVER")
        self.server = TCPServer(self.onImageReceived)
        self.server.start(server_ip, server_port)
    
    def run(self):
        self.server.listen()

    def onImageReceived(self, image_data: bytes):
        img: Image = bytesToImage(image_data)
        print("image received")
        # img.show("Received image")

    def close(self):
        if self.server:
            self.server.close()
