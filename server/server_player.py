from model.player import AbstractPlayer

class ServerPlayer(AbstractPlayer):

    def __init__(self, x, y, radius, offset, game, player_id):
        super().__init__(x, y, radius, offset, game, player_id)
        self.was_updated = False