import socket
import settings
from udp_communication.messages.game_state_pb2 import GameState


class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def run(self):
        # while True:
        game_state = GameState()
        player = game_state.players.add()
        player.id = 1
        player.x = 35
        player.y = 125
        player.health = 100
        player.direction = 'LEFT'
        player.speed = 10
        projectile = game_state.projectiles.add()
        projectile.id = 3
        projectile.x = 15
        projectile.y = 16
        projectile.damage = 5
        projectile.speed = 13
        projectile.owner_id = 1
        message = game_state.SerializeToString()
        len(message)
        self.socket.sendto(message, (settings.SERVER_HOST, settings.SERVER_PORT))
