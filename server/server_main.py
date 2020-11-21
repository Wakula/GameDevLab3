import socket
import settings
import threading
import time
import model.udp_helper as udp_helper
from model.constants import Directions
from server.server_game import ServerGame
from udp_communication.communication import UDPCommunicator
from udp_communication.messages import messages_pb2


class Server:
    def __init__(self):
        self.udp_communicator = UDPCommunicator(settings.SERVER_HOST, settings.SERVER_PORT)
        self.game = ServerGame()
        self.clients = []

    def time(self):
        return time.time()

    def handle_client_message(self, message, host, port):
        if isinstance(message, messages_pb2.GameStartedOk):
            game_state = self.game.create_game_state()
            self.udp_communicator.send(game_state, host, port)

        elif isinstance(message, messages_pb2.PlayerState):
            player_id = message.player_id
            self.game.update_player_position(player_id, message.x, message.y, Directions(message.direction))
            updated_player = self.game.get_player(player_id)
            updated_player_state = udp_helper.create_player_state(updated_player)
            for client in self.clients:
                if client.player_id != player_id:
                    self.udp_communicator.send(updated_player_state, client.host, client.port)
        elif isinstance(message, messages_pb2.ShootEvent):
            player_id = message.player_id
            owner = self.game.get_player(player_id)
            projectile = udp_helper.create_projectile(message, owner)
            self.game.projectiles.append(projectile)
            for client in self.clients:
                if client.player_id == player_id:
                    self.udp_communicator.send_until_approval(messages_pb2.ShootOk(), client.host, client.port)
                else:
                    shoot_event = udp_helper.create_shoot_event(projectile)
                    self.udp_communicator.send_until_approval(shoot_event, client.host, client.port)

    def create_room(self):
        while len(self.clients) < settings.CLIENTS_AMOUNT:
            address_to_messages = self.udp_communicator.read()
            if not address_to_messages:
                continue
            for address, messages in address_to_messages.items():
                for message in messages:
                    if any(map(lambda c: c.player_id == message.player_id, self.clients)):
                        continue
                    if isinstance(message, messages_pb2.Connect):
                        self.game.init_player(message.player_id)
                        self.clients.append(Client(*address, message.player_id))
                        break
        for client in self.clients:
            game_started = messages_pb2.GameStarted()
            self.udp_communicator.send_until_approval(game_started, client.host, client.port)
            game_state = self.game.create_game_state()
            self.udp_communicator.send(game_state, client.host, client.port)

    def run(self):
        self.create_room()
        while True:
            address_to_messages = self.udp_communicator.read()
            if address_to_messages:
                for address, messages in address_to_messages.items():
                    host, port = address
                    for message in messages:
                        self.handle_client_message(message, host, port)

            self.send_player_states()
            self.game.run()

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
