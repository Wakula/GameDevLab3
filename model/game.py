import random
import pygame
import settings
from model import boosts


class AbstractGame:
    BOOSTS = (
        boosts.HealthBoost,
        boosts.ProjectileSpeedBoost,
        boosts.PlayerSpeedBoost,
        boosts.PlayerDamageBoost,
    )

    def __init__(self):
        pygame.init()
        self.game_over = False
        self.players = []
        self.projectiles = []
        self.boosts_on_field = []
        self.attached_boosts = []
        self.clock = pygame.time.Clock()

    @property
    def objects(self):
        # TODO: maybe chain is better
        return (*self.players, *self.projectiles, *self.boosts_on_field)

    def update_player_position(self, player_id, new_x, new_y):
        for player in self.players:
            if player.player_id == player_id:
                player.x = new_x
                player.y = new_y
    
    def update_player_health(self, player_id, new_health):
        for player in self.players:
            if player.player_id == player_id:
                player.health = new_health

    def handle_projectile_collisions(self):
        collided_projectiles = []
        dead_players = []
        for projectile in self.projectiles:
            for player in self.players:
                if player is projectile.owner:
                    continue
                if player.bounds.colliderect(projectile.bounds):
                    self.on_player_hit(projectile, player, dead_players)
                    collided_projectiles.append(projectile)
            if projectile not in collided_projectiles and projectile.is_out_of_bounds():
                collided_projectiles.append(projectile)
        for projectile in collided_projectiles:
            self.projectiles.remove(projectile)
        for player in dead_players:
            self.players.remove(player)

    def handle_boosts_collisions(self):
        removed_boosts_from_field = []
        for boost in self.boosts_on_field:
            for player in self.players:
                if player.bounds.colliderect(boost.bounds):
                    boost.attach_to_player(player)
                    boost.apply_effect()
                    self.attached_boosts.append(boost)
                    removed_boosts_from_field.append(boost)
        for boost in removed_boosts_from_field:
            self.boosts_on_field.remove(boost)

    def try_undo_boosts_effects(self):
        undone_boosts = []
        for boost in self.attached_boosts:
            boost.try_undo_effect()
            if boost.is_effect_undone():
                undone_boosts.append(boost)
        for boost in undone_boosts:
            self.attached_boosts.remove(boost)

    def spawn_boosts(self):
        print("NOPE")
        if len(self.boosts_on_field) == settings.MAX_BOOSTS_ON_FIELD:
            return
        # TODO: rework random for boost geneartion
        if random.randint(0, 100):
            return
        boost_cls = random.choice(self.BOOSTS)
        boost = boost_cls(
            x=random.randint(0, settings.SCREEN_WIDTH-settings.BOOST_WIDTH),
            y=random.randint(0, settings.SCREEN_HEIGHT-settings.BOOST_HEIGHT),
            w=settings.BOOST_HEIGHT,
            h=settings.BOOST_WIDTH,
        )
        self.boosts_on_field.append(boost)


    def on_player_hit(self, projectile, player, dead_players):
        projectile.hit(player)
        if player.health <= 0:
            dead_players.append(player)

    def get_ticks(self):
        return pygame.time.get_ticks()
