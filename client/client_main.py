import socket
import settings
import pygame
import time
import model.udp_helper as udp_helper
from client.client_game import ClientGame
from model.constants import Directions
from udp_communication.messages.messages_pb2 import Connect, GameStartedOk, GameStarted, PlayerState, GameState
from udp_communication.communication import UDPCommunicator


class Client:
    def __init__(self, player_id):
        self.udp_communicator = UDPCommunicator('127.0.0.1')
        self.player_id = player_id
        self.game = ClientGame()

    def run(self):
        self.game.show_start_screen()
        self.game.show_connecting()
        self.connect_to_server()
        while not self.game.game_over:
            self.read_socket()
            self.send_state()
            self.game.run()

    def connect_to_server(self):
        connect = Connect()
        connect.player_id = self.player_id
        self.udp_communicator.send_until_approval(connect, settings.SERVER_HOST, settings.SERVER_PORT)
        address_to_messages = None
        while not address_to_messages:
            address_to_messages = self.udp_communicator.read()
        address, messages = address_to_messages.popitem()
        for message in messages:
            if isinstance(message, GameStarted) and address == (settings.SERVER_HOST, settings.SERVER_PORT):
                game_started_ok = GameStartedOk()
                game_started_ok.player_id = self.player_id
                game_state = self.udp_communicator.send_until_approval(game_started_ok, settings.SERVER_HOST, settings.SERVER_PORT)
                self.init_game(game_state)
    
    def send_state(self):
        player = self.game.get_player(self.player_id)
        if player:
            player_state = udp_helper.create_player_state(player)
            self.udp_communicator.send(player_state, settings.SERVER_HOST, settings.SERVER_PORT)

    def init_game(self, game_state):
        for player in game_state.players:
            if self.player_id == player.player_id:
                self.game.init_client_player(player.x, player.y, Directions(player.direction), player.player_id)
            else:
                self.game.init_network_opponent(player.x, player.y, Directions(player.direction), player.player_id)

    def read_socket(self):
        address_to_messages = self.udp_communicator.read()
        if not address_to_messages:
            return
        address, messages = address_to_messages.popitem()
        for message in messages:
            if isinstance(message, PlayerState):
                player_id = message.player_id
                if not self.game.player_exists(player_id):
                    if self.player_id == player_id:
                        self.game.init_client_player(message.x, message.y, Directions(message.direction), message.player_id)
                    else:
                        self.game.init_network_opponent(message.x, message.y, Directions(message.direction), message.player_id)

                if message.player_id != self.player_id:
                    self.game.update_player_position(message.player_id, message.x, message.y, Directions(message.direction))
