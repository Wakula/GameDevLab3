from collections import defaultdict
from model.game import AbstractGame
from server.server_player import ServerPlayer
from udp_communication.messages.messages_pb2 import PlayerState, GameState
import settings
import random
import model.udp_helper as udp_helper
from model import boosts


class ServerGame(AbstractGame):
    BOOSTS = (
        boosts.HealthBoost,
        boosts.ProjectileSpeedBoost,
        boosts.PlayerSpeedBoost,
        boosts.PlayerDamageBoost,
    )

    def __init__(self):
        super().__init__()
        self.spawned_boost = None
        self.removed_boosts = None
        self.boost_id = 1

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
            self.players[player_id] = player

    def spawn_boosts(self):
        if len(self.boosts_on_field) == settings.MAX_BOOSTS_ON_FIELD:
            return
        # TODO: rework random for boost geneartion
        if random.randint(0, 100):
            return
        boost_cls = random.choice(self.BOOSTS)

        boost = boost_cls(
            boost_id=self.boost_id,
            x=random.randint(0, settings.SCREEN_WIDTH-settings.BOOST_WIDTH),
            y=random.randint(0, settings.SCREEN_HEIGHT-settings.BOOST_HEIGHT),
            w=settings.BOOST_HEIGHT,
            h=settings.BOOST_WIDTH,
        )
        self.boost_id += 1
        self.boosts_on_field[boost.boost_id] = boost
        self.spawned_boost = boost

    def handle_boosts_collisions(self):
        removed_boosts_from_field = []
        for boost in self.boosts_on_field.values():
            for player in self.players.values():
                if player.bounds.colliderect(boost.bounds):
                    boost.attach_to_player(player)
                    boost.apply_effect()
                    self.attached_boosts.append(boost)
                    removed_boosts_from_field.append(boost)
        for boost in removed_boosts_from_field:
            del self.boosts_on_field[boost.boost_id]
        self.removed_boosts = removed_boosts_from_field

    def try_undo_boosts_effects(self):
        undone_boosts = []
        for boost in self.attached_boosts:
            boost.try_undo_effect()
            if boost.is_effect_undone():
                undone_boosts.append(boost)
        for boost in undone_boosts:
            self.attached_boosts.remove(boost)

    def update(self):
        for game_object in self.objects:
            game_object.update()
        self.spawn_boosts()
        self.handle_boosts_collisions()
        self.try_undo_boosts_effects()
        self.handle_projectile_collisions()

    def run(self):
        self.update()
        self.clock.tick(settings.FRAME_RATE)

    def create_game_state(self):
        game_state = GameState()
        for player in self.players.values():
            player_state = udp_helper.create_player_state(player)
            game_state.players.append(player_state)
        return game_state
