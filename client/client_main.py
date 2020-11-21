from itertools import chain
import settings
import model.udp_helper as udp_helper
from client.client_game import ClientGame
from model.constants import Directions
from udp_communication.messages import messages_pb2
from udp_communication.communication import UDPCommunicator


class Client:
    def __init__(self, player_id):
        self.udp_communicator = UDPCommunicator('127.0.0.1', is_client=True)
        self.player_id = player_id

    def run(self):
        while True:
            self.game = ClientGame()
            self.game.show_start_screen()
            self.game.show_connecting()
            self.connect_to_server()
            while not self.game.is_game_over() and not self.player_id in self.game.dead_players:
                self.read_socket()
                self.send_actions()
                self.game.run()
            is_client_winner = self.game.player_exists(self.player_id)
            self.game.show_end_screen(is_client_winner)

    def connect_to_server(self):
        connect = messages_pb2.Connect()
        connect.player_id = self.player_id
        self.udp_communicator.send_until_approval(connect, settings.SERVER_HOST, settings.SERVER_PORT)
        address_to_messages = None
        while not address_to_messages:
            address_to_messages = self.udp_communicator.read()
        address, messages = address_to_messages.popitem()
        for message in chain(*messages.values()):
            if isinstance(message, messages_pb2.GameStarted) and address == (settings.SERVER_HOST, settings.SERVER_PORT):
                game_started_ok = messages_pb2.GameStartedOk()
                game_started_ok.player_id = self.player_id
                game_state = self.udp_communicator.send_until_approval(game_started_ok, settings.SERVER_HOST, settings.SERVER_PORT)
                self.init_game(game_state)

    def send_actions(self):
        if self.player_id in self.game.dead_players:
            #TODO: return to main menu
            return
        player = self.game.players[self.player_id]
        if player:
            self.send_shoot_event(player)
            self.send_state(player)

    def send_state(self, player):
        player_state = udp_helper.create_player_state(player)
        self.udp_communicator.send(player_state, settings.SERVER_HOST, settings.SERVER_PORT)

    def send_shoot_event(self, player):
        if not player.shot_projectile:
            return
        shoot_event = udp_helper.create_shoot_event(player.shot_projectile)
        self.udp_communicator.send_until_approval(shoot_event, settings.SERVER_HOST, settings.SERVER_PORT)
        player.shot_projectile = None

    def init_game(self, game_state):
        for player in game_state.players:
            if self.player_id == player.player_id:
                self.game.init_client_player(player.x, player.y, Directions(player.direction), player.player_id)
            else:
                self.game.init_network_opponent(player.x, player.y, Directions(player.direction), player.player_id)

    def handle_message(self, message):
        if isinstance(message, messages_pb2.PlayerState):
            player_id = message.player_id
            if player_id in self.game.dead_players:
                return
            if not self.game.player_exists(player_id):
                if self.player_id == player_id:
                    self.game.init_client_player(message.x, message.y, Directions(message.direction), message.player_id)
                else:
                    self.game.init_network_opponent(message.x, message.y, Directions(message.direction),
                                                    message.player_id)

            if message.player_id != self.player_id:
                self.game.update_player_position(message.player_id, message.x, message.y, Directions(message.direction))
            self.game.update_player_health(player_id, message.health)

        elif isinstance(message, messages_pb2.ShootEvent):
            if message.player_id in self.game.dead_players:
                return
            if not (message.player_id, message.projectile_id) in self.game.projectiles.keys():
                owner = self.game.players[message.player_id]
                projectile = udp_helper.create_projectile(message, owner)
                self.game.projectiles[projectile.id] = projectile
                self.udp_communicator.send_until_approval(messages_pb2.ShootOk(), settings.SERVER_HOST, settings.SERVER_PORT)

        elif isinstance(message, messages_pb2.PlayerIsDead):
            if message.player_id not in self.game.dead_players:
                self.game.dead_players[message.player_id] = self.game.players[message.player_id]
                del self.game.players[message.player_id]
            self.udp_communicator.send_until_approval(
                messages_pb2.PlayerIsDeadOk(), settings.SERVER_HOST, settings.SERVER_PORT
            )

        elif isinstance(message, messages_pb2.Boost):
            boost = udp_helper.create_boost(message)
            self.game.boosts_on_field.append(boost)
            self.udp_communicator.send_until_approval(
                messages_pb2.BoostOk(), settings.SERVER_HOST, settings.SERVER_PORT
            )

    def read_socket(self):
        address_to_messages = self.udp_communicator.read()
        if not address_to_messages:
            return
        address, messages = address_to_messages.popitem()
        for message in chain(*messages.values()):
            self.handle_message(message)
