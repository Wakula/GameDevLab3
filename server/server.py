import socket
import settings


class Server:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((settings.SERVER_HOST, settings.SERVER_PORT))

    def run(self):
        while True:
            data, address = self.socket.recvfrom(1024)
            print(data, address)
