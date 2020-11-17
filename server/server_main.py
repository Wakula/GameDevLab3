import socket
import settings
import threading
import time
from model.constants import Directions
from server.server_game import ServerGame
from udp_communication.communication import UDPCommunicator
from udp_communication.messages.messages_pb2 import Connect, GameStarted, GameStartedOk, PlayerState


class Server:
    def __init__(self):
        read_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        write_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        read_sock.bind((settings.SERVER_HOST, settings.SERVER_PORT))
        write_sock.bind((settings.SERVER_HOST, 0))
        self.udp_communicator = UDPCommunicator(read_sock, write_sock)
        self.game = ServerGame()
        self.clients = []

    def time(self):
        return time.time()

    def run(self):
        #start_time = self.time()
        #message, address = self.udp_communicator.read()
        #host, port = address
        while True:
            message, address = self.udp_communicator.read()
            host, port = address
            if isinstance(message, Connect):
                print("hello")
                game_started = GameStarted()
                self.udp_communicator.send_until_approval(game_started, host, port)
                self.game.init_player(message.player_id)
                new_player = self.game.get_player(message.player_id)
                player_state = self.create_player_state(new_player)
                self.udp_communicator.send(player_state, host, port)
                self.clients.append(Client(host, port, message.player_id))
            
            elif isinstance(message, PlayerState):
                player_id = message.player_id
                self.game.update_player_position(player_id, message.x, message.y, Directions(message.direction))
                updated_player = self.game.get_player(player_id)
                updated_player_state = self.create_player_state(updated_player)
                for client in self.clients:
                    if client.player_id != player_id:
                        self.udp_communicator.send(updated_player_state, client.host, client.port)
        
            self.send_player_states()
            self.game.run()

        #delta_time = self.time() - start_time
        #delta_time = 1/settings.SERVER_FREQ - delta_time
        #threading.Timer(delta_time, self.run).start()

    def send_player_states(self):
        for player in self.game.players:
            player_state = self.create_player_state(player)
            for client in self.clients:
                self.udp_communicator.send(player_state, client.host, client.port)

    def create_player_state(self, player):
        playerState = PlayerState()
        playerState.player_id = player.player_id 
        playerState.x = player.bounds.x 
        playerState.y = player.bounds.y 
        playerState.direction = player.direction.value
        return playerState

class Client:

    def __init__(self, host, port, player_id):
        self.host = host
        self.port = port
        self.player_id = player_id