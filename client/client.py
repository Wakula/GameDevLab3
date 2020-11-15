import socket
import settings


class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def run(self):
        while True:
            self.socket.sendto(b'Ow shit im sorry', (settings.SERVER_HOST, settings.SERVER_PORT))
