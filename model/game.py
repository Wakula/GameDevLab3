from collections import defaultdict
import pygame
import settings


class AbstractGame:
    def __init__(self):
        pygame.init()
        self.game_over = False
        self.players = []
        self.projectiles = []
        self.clock = pygame.time.Clock()

    @property
    def objects(self):
        return (*self.players, *self.projectiles)

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
        self.remove_objects(collided_projectiles, dead_players)

    def on_player_hit(self, projectile, player, dead_players):
        projectile.hit(player)
        if player.health <= 0:
            dead_players.append(player)

    def remove_objects(self, collided_projectiles, dead_players):
        for projectile in collided_projectiles:
            self.projectiles.remove(projectile)
        for player in dead_players:
            self.players.remove(player)

    def get_ticks(self):
        return pygame.time.get_ticks()

