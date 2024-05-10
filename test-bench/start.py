import sys
import logging
from infrastructure.middle import AccessPoint
from infrastructure.sender import SendingClient
from network.connection import Protocol, ConnectionProvider

PORT = 10060
PROTOCOL = Protocol.TCP
main_instance = None


def main():

    initLogging()

    if 2 <= len(sys.argv) <= 3 and sys.argv[1] == "server":
        server_ip = sys.argv[2] if len(sys.argv) > 2 else ""

        connection = ConnectionProvider(server_ip, PORT, PROTOCOL)
        main_instance = AccessPoint(connection)
        main_instance.start()

        print("Access point ready. Accepting connections...")
        main_instance.shutdownBarrier()

    elif len(sys.argv) == 3 and sys.argv[1] == "client":
        server_ip = sys.argv[2]

        connection = ConnectionProvider(server_ip, PORT, PROTOCOL)
        main_instance = SendingClient(connection)
        main_instance.start()
        main_instance.shutdownBarrier()

    else:
        print("Usage: <{client|server}> <server_ip>")


def initLogging():
    logging.basicConfig(
        filename="output.log",
        level=logging.DEBUG,
        format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Suppress PIL debug messages (https://github.com/ManimCommunity/manim/issues/363)
    logging.getLogger("PIL").setLevel(logging.INFO)


if __name__ == "__main__":

    try:
        main()
    finally:
        print("\nClosing...")
        if main_instance:
            main_instance.close()
        print("Everything closed.")
