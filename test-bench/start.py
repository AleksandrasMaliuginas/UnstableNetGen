import sys
from infrastructure.middle import AccessPoint
from infrastructure.sender import SendingClient
from compression import NoopEncoder

PORT = 10060
main_instance = None


def main():

    if 2 <= len(sys.argv) <= 3 and sys.argv[1] == "server":
        server_ip = sys.argv[2] if len(sys.argv) > 2 else ""

        main_instance = AccessPoint(server_ip=server_ip, server_port=PORT)
        main_instance.start()

        print("Access point ready. Accepting connections...")
        main_instance.shutdownBarrier()

    elif len(sys.argv) == 3 and sys.argv[1] == "client":
        server_ip = sys.argv[2]

        main_instance = SendingClient(server_ip=server_ip, server_port=PORT, encoder=NoopEncoder())
        main_instance.start()
        main_instance.shutdownBarrier()

    else:
        print("Usage: <{client|server}> <server_ip>")


if __name__ == "__main__":

    try:
        main()
    finally:
        print("\nClosing...")
        if main_instance:
            main_instance.close()
        print("Everything closed.")
