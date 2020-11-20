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

    def update_player_position(self, player_id, new_x, new_y, new_dir):
        was_updated = False
        for player in self.players:
            if player.player_id == player_id:
                dx = new_x - player.bounds.x
                dy = new_y - player.bounds.y
                player.move(dx, dy)
                prev_dir = player.direction
                player.direction = new_dir
                was_updated = dx != 0 or dy != 0 or new_dir != prev_dir
        return was_updated
    
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

    def player_exists(self, player_id):
        return any(map(lambda p: p.player_id == player_id, self.players))
    
    def get_player(self, player_id):
        for player in self.players:
            if player.player_id == player_id:
                return player
