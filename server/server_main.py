import socket
import settings
import threading
import time
import model.udp_helper as udp_helper
from model.constants import Directions
from server.server_game import ServerGame
from udp_communication.communication import UDPCommunicator
from udp_communication.messages.messages_pb2 import Connect, GameStarted, GameStartedOk, PlayerState


class Server:
    def __init__(self):
        self.udp_communicator = UDPCommunicator((settings.SERVER_HOST, settings.SERVER_PORT))
        self.game = ServerGame()
        self.clients = []

    def time(self):
        return time.time()

    def run(self):
        while True:
            message, address = self.udp_communicator.read()
            host, port = address
            if isinstance(message, Connect):
                game_started = GameStarted()
                self.udp_communicator.send_until_approval(game_started, host, port)
                self.game.init_player(message.player_id)
                self.clients.append(Client(host, port, message.player_id))
                game_state = self.game.create_game_state()
                self.udp_communicator.send(game_state, host, port)
            
            elif isinstance(message, GameStartedOk):
                game_state = self.game.create_game_state()
                self.udp_communicator.send(game_state, host, port)

            elif isinstance(message, PlayerState):
                player_id = message.player_id
                self.game.update_player_position(player_id, message.x, message.y, Directions(message.direction))
                updated_player = self.game.get_player(player_id)
                updated_player_state = udp_helper.create_player_state(updated_player)
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
            player_state = udp_helper.create_player_state(player)
            for client in self.clients:
                if client.player_id != player_state.player_id:
                    self.udp_communicator.send(player_state, client.host, client.port)

class Client:

    def __init__(self, host, port, player_id):
        self.host = host
        self.port = port
        self.player_id = player_id