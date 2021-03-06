import settings
from itertools import chain
import model.udp_helper as udp_helper
from model.constants import Directions
from server.server_game import ServerGame
from udp_communication.communication import UDPCommunicator
from udp_communication.messages import messages_pb2


class Server:
    def __init__(self):
        self.udp_communicator = UDPCommunicator(settings.SERVER_HOST, settings.SERVER_PORT)

    def init_server(self):
        self.udp_communicator.clean_sockets()
        self.game = ServerGame()
        self.clients = {}
        self.dead_clients = {}

    def handle_client_message(self, message, host, port):
        if message.player_id in self.game.dead_players:
            return
        if isinstance(message, messages_pb2.GameStartedOk):
            game_state = self.game.create_game_state()
            self.udp_communicator.send(game_state, host, port)

        elif isinstance(message, messages_pb2.PlayerState):
            player_id = message.player_id
            self.game.update_player_position(player_id, message.x, message.y, Directions(message.direction))
            updated_player = self.game.players[player_id]
            updated_player_state = udp_helper.create_player_state(updated_player)
            for client in self.clients.values():
                self.udp_communicator.send(updated_player_state, client.host, client.port)

        elif isinstance(message, messages_pb2.ShootEvent):
            player_id = message.player_id
            owner = self.game.players[player_id]
            projectile = udp_helper.create_projectile(message, owner)
            self.game.projectiles[projectile.id] = projectile
            for client in self.clients.values():
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
                for message in chain(*messages.values()):
                    if message.player_id in self.clients:
                        continue
                    if isinstance(message, messages_pb2.Connect):
                        self.game.init_player(message.player_id)
                        self.clients[message.player_id] = Client(*address, message.player_id)
                        break
        
        for client in self.clients.values():
            game_started = messages_pb2.GameStarted()
            self.udp_communicator.send_until_approval(game_started, client.host, client.port)
            game_state = self.game.create_game_state()
            self.udp_communicator.send(game_state, client.host, client.port)

    def run(self):
        while True:
            self.init_server()
            self.create_room()
            while not self.game.is_game_over():
                address_to_messages = self.udp_communicator.read()
                if address_to_messages:
                    for address, messages in address_to_messages.items():
                        host, port = address
                        for message in chain(*messages.values()):
                            self.handle_client_message(message, host, port)
                self.send_player_states()
                self.send_dead_player_states()
                self.send_boosts()
                self.game.run()

    def send_dead_player_states(self):
        for dead_player_id in self.game.dead_players:
            if dead_player_id not in self.dead_clients:
                for client in self.clients.values():
                    player_is_dead = udp_helper.create_dead_player_state(dead_player_id)
                    self.udp_communicator.send_until_approval(player_is_dead, client.host, client.port)
        
        self.clean_dead_clients()

    def clean_dead_clients(self):
        for player_id in self.game.dead_players:
            if player_id in self.clients:
                self.dead_clients[player_id] = self.clients[player_id]
                del self.clients[player_id]

    def send_player_states(self):
        for player in self.game.players.values():
            player_state = udp_helper.create_player_state(player)
            for client in self.clients.values():
                if client.player_id != player_state.player_id:
                    self.udp_communicator.send(player_state, client.host, client.port)
            for dead_client in self.dead_clients.values():
                self.udp_communicator.send(player_state, dead_client.host, dead_client.port)
    
    def send_boosts(self):
        
        if self.game.spawned_boost:
            boost_message = udp_helper.create_boost_message(self.game.spawned_boost)
            for client in self.clients.values():
                self.udp_communicator.send_until_approval(boost_message, client.host, client.port)
            self.game.spawned_boost = None

        if self.game.removed_boosts:
            for removed_boost in self.game.removed_boosts:
                pick_up_message = udp_helper.create_boost_pick_up_message(removed_boost)
                for client in self.clients.values():
                    self.udp_communicator.send_until_approval(pick_up_message, client.host, client.port)
            self.game.removed_boosts = None

class Client:
    def __init__(self, host, port, player_id):
        self.host = host
        self.port = port
        self.player_id = player_id
