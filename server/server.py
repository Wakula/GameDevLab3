import socket
import settings
from udp_communication.messages.game_state_pb2 import GameState


class Server:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((settings.SERVER_HOST, settings.SERVER_PORT))

    def run(self):
        while True:
            game_state = GameState()
            data, address = self.socket.recvfrom(1024)
            game_state.ParseFromString(data)
            print(game_state, address)
