from model.constants import Directions, DIRECTIONS_TO_DELTA
from model.game_object import GameObject
import pygame


class Projectile(GameObject):

    def __init__(self, x, y, radius, color, speed, player_direction):
        self.radius = radius
        self.diameter = 2 * radius
        self.color = color
        x_direction, y_direction = DIRECTIONS_TO_DELTA[player_direction]
        dx, dy = x_direction * speed, y_direction * speed
        super().__init__(x - radius, y - radius, self.diameter, self.diameter, (dx, dy))

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.bounds.center, self.radius)
