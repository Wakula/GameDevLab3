import socket
import settings
from udp_communication.messages.messages_pb2 import Connect, GameStartedOk, GameStarted
from udp_communication.communication import UDPCommunicator


class Client:
    def __init__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('127.0.0.1', 0))
        self.udp_communicator = UDPCommunicator(sock)

    def run(self):
        connect = Connect()
        self.udp_communicator.send_until_approval(connect, settings.SERVER_HOST, settings.SERVER_PORT)
        message, address = self.udp_communicator.read()
        if isinstance(message, GameStarted) and address == (settings.SERVER_HOST, settings.SERVER_PORT):
            game_started_ok = GameStartedOk()
            self.udp_communicator.send_until_approval(game_started_ok, settings.SERVER_HOST, settings.SERVER_PORT)
