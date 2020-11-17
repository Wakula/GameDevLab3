from collections import defaultdict
from model.game import AbstractGame
import settings

class ServerGame(AbstractGame):
    def __init__(self):
        super.__init__()

    def init_player(self, player_id):
        pass

    def update(self, game_state):
        for game_object in self.objects:
            game_object.update()
        self.handle_projectile_collisions()