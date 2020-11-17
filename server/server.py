import socket
import settings
from udp_communication.communication import UDPCommunicator
from udp_communication.messages.messages_pb2 import Connect, GameStarted, GameStartedOk


class Server:
    def __init__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((settings.SERVER_HOST, settings.SERVER_PORT))
        self.udp_communicator = UDPCommunicator(sock)

    def run(self):
        while True:
            message, address = self.udp_communicator.read()
            host, port = address
            if isinstance(message, Connect):
                game_started = GameStarted()
                self.udp_communicator.send_until_approval(game_started, host, port)
                print('SUCCESS')
