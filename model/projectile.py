from model.constants import DIRECTIONS_TO_DELTA
from model.game_object import GameObject
import settings
import pygame


class Projectile(GameObject):
    projectile_count = 0

    def __init__(self, x, y, radius, color, speed, owner, damage):
        self.radius = radius
        self.diameter = 2 * radius
        self.color = color
        x_direction, y_direction = DIRECTIONS_TO_DELTA[owner.direction]
        self.owner = owner
        self.damage = damage
        Projectile.projectile_count += 1
        self.id = (owner.player_id, Projectile.projectile_count)
        dx, dy = x_direction * speed, y_direction * speed
        super().__init__(x - radius, y - radius, self.diameter, self.diameter, (dx, dy))

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.bounds.center, self.radius)

    def is_out_of_bounds(self):
        if (
            self.bounds.top > settings.SCREEN_HEIGHT
            or self.bounds.top < 0
            or self.bounds.left < 0
            or self.bounds.right > settings.SCREEN_WIDTH
        ):
            return True
        return False

    def hit(self, player):
        player.health -= self.damage
