import socket
import settings
from client.client_game import ClientGame
from model.constants import Directions
from udp_communication.messages.messages_pb2 import Connect, GameStartedOk, GameStarted, PlayerState
from udp_communication.communication import UDPCommunicator


class Client:
    def __init__(self, player_id):
        read_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        read_sock.bind(('127.0.0.1', 0))
        write_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        write_sock.bind(('127.0.0.1', 0))
        self.udp_communicator = UDPCommunicator(read_sock, write_sock)
        self.player_id = player_id
        self.game = ClientGame()

    def run(self):
        self.connect_to_server()
        while not self.game.game_over:
            self.read_socket()
            self.game.run()
            self.send_state()

    def connect_to_server(self):
        connect = Connect()
        connect.player_id = self.player_id
        self.udp_communicator.send_until_approval(connect, settings.SERVER_HOST, settings.SERVER_PORT)
        message, address = self.udp_communicator.read()
        if isinstance(message, GameStarted) and address == (settings.SERVER_HOST, settings.SERVER_PORT):
            game_started_ok = GameStartedOk()
            game_started_ok.player_id = self.player_id
            self.udp_communicator.send(game_started_ok, settings.SERVER_HOST, settings.SERVER_PORT)
    
    def send_state(self):
        player = self.game.get_player(self.player_id)
        if player:
            player_state = self.create_player_state(player)
            self.udp_communicator.send(player_state, settings.SERVER_HOST, settings.SERVER_PORT)
    
    def create_player_state(self, player):
        playerState = PlayerState()
        playerState.player_id = player.player_id 
        playerState.x = player.bounds.x 
        playerState.y = player.bounds.y 
        playerState.direction = player.direction.value
        return playerState

    def read_socket(self):
        message, address = self.udp_communicator.read()
        if isinstance(message, PlayerState):
            player_id = message.player_id
            if not self.game.player_exists(player_id):
                if self.player_id == player_id:
                    self.game.init_client_player(message.x, message.y, Directions(message.direction), message.player_id)
                else:
                    self.game.init_network_opponent(message.x, message.y, Directions(message.direction), message.player_id)
            else:
                if message.player_id != self.player_id:
                    self.game.update_player_position(message.player_id, message.x, message.y, Directions(message.direction))   