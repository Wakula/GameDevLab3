import random
import pygame
import settings


class AbstractGame:
    def __init__(self):
        pygame.init()
        self.game_over = False
        self.players = {}
        self.projectiles = {}
        self.boosts_on_field = []
        self.attached_boosts = []
        self.clock = pygame.time.Clock()
        self.dead_players = set()

    @property
    def objects(self):
        return (*self.players.values(), *self.projectiles.values(), *self.boosts_on_field)

    def update_player_position(self, player_id, new_x, new_y, new_dir):
        player = self.players[player_id]
        dx = new_x - player.bounds.x
        dy = new_y - player.bounds.y
        player.move(dx, dy)
        player.direction = new_dir
    
    def update_player_health(self, player_id, new_health):
        player = self.players[player_id]
        player.health = new_health

    def handle_projectile_collisions(self):
        collided_projectiles = []
        dead_players = []
        for projectile in self.projectiles.values():
            for player in self.players.values():
                if player is projectile.owner:
                    continue
                if player.bounds.colliderect(projectile.bounds):
                    self.on_player_hit(projectile, player, dead_players)
                    collided_projectiles.append(projectile)
            if projectile not in collided_projectiles and projectile.is_out_of_bounds():
                collided_projectiles.append(projectile)
        for projectile in collided_projectiles:
            del self.projectiles[projectile.id]
        for player in dead_players:
            del self.players[player.player_id]

    def handle_boosts_collisions(self):
        removed_boosts_from_field = []
        for boost in self.boosts_on_field:
            for player in self.players.values():
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

    def on_player_hit(self, projectile, player, dead_players):
        projectile.hit(player)
        if player.health <= 0:
            self.dead_players.add(player.player_id)
            dead_players.append(player)

    def remove_objects(self, collided_projectiles, dead_players):
        for projectile in collided_projectiles:
            del self.projectiles[projectile.id]
        for player in dead_players:
            del self.players[player.player_id]

    def get_ticks(self):
        return pygame.time.get_ticks()

    def player_exists(self, player_id):
        return player_id in self.players.keys()
