from collections import defaultdict
from model.game import AbstractGame
from server.server_player import ServerPlayer
import settings
import random

class ServerGame(AbstractGame):
    def __init__(self):
        super().__init__()

    def init_player(self, player_id):
        if not self.player_exists(player_id):
            x_spawn = random.randint(2*settings.PLAYER_RADIUS, settings.SCREEN_WIDTH - 2*settings.PLAYER_RADIUS)
            y_spawn = random.randint(2*settings.PLAYER_RADIUS, settings.SCREEN_HEIGHT - 2*settings.PLAYER_RADIUS)
            player = ServerPlayer(
                x_spawn,
                y_spawn,
                settings.PLAYER_RADIUS,
                settings.PLAYER_SPEED,
                self,
                player_id
            )
            self.players.append(player)

    def update(self):
        for game_object in self.objects:
            game_object.update()
        self.handle_projectile_collisions()
    
    def run(self):
        self.update()
        self.clock.tick(settings.FRAME_RATE)