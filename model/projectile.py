from model.constants import Directions
from model.game_object import GameObject
import pygame


class Projectile(GameObject):
    DIRECTIONS_TO_DELTA = {
        Directions.LEFT: (-1, 0),
        Directions.UP: (0, -1),
        Directions.RIGHT: (1, 0),
        Directions.DOWN: (0, 1)
    }

    def __init__(self, x, y, radius, color, speed, player_direction):
        self.radius = radius
        self.diameter = 2 * radius
        self.color = color
        x_direction, y_direction = self.DIRECTIONS_TO_DELTA[player_direction]
        dx, dy = x_direction * speed, y_direction * speed
        super().__init__(x - radius, y - radius, self.diameter, self.diameter, (dx, dy))

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.bounds.center, self.radius)
