import socket, sys
from PIL import Image
from SendingClient import SendingClient
from network.tcp import TCPServer, TCPClient
from imageUtils import bytesToImage
from generativeAI import NoopEncoder

dgram_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
PORT = 1060

if __name__ == "__main__":

    if 2 <= len(sys.argv) <= 3 and sys.argv[1] == "server":
        server_ip = sys.argv[2] if len(sys.argv) > 2 else ""

        def image_handler(image_data: bytes):
            img: Image = bytesToImage(image_data)
            img.show("Received image")

        server = TCPServer(image_handler)
        server.start(server_ip, PORT)
        server.listen()

    elif len(sys.argv) == 3 and sys.argv[1] == "client":
        server_ip = sys.argv[2]

        SendingClient(
            client=TCPClient(),
            server_ip=server_ip,
            server_port=PORT,
            encoder=NoopEncoder(),
        ).start()

    else:
        print("Usage: <{client|server}> <server_ip>")
