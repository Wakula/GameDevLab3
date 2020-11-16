from model.constants import Directions
from model.game_object import GameObject
import pygame
import settings

class Player(GameObject):
    KEYS_TO_DIRECTIONS = {
        pygame.K_a: Directions.LEFT,
        pygame.K_w: Directions.UP,
        pygame.K_d: Directions.RIGHT,
        pygame.K_s: Directions.DOWN
    }

    def __init__(self, x, y, radius, color, offset):
        self.offset = offset
        self.radius = radius
        self.diameter = 2 * radius
        super().__init__(x-radius, y-radius, self.diameter, self.diameter)
        self.color = color
        self.direction = Directions.UP
        self.is_moving = False

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.bounds.center, self.radius)

    def handle(self, key):
        self.is_moving = not self.is_moving
        if key in self.KEYS_TO_DIRECTIONS.keys() and self.is_moving:
            self.direction = self.KEYS_TO_DIRECTIONS[key] 

    def update(self):
        if self.direction == Directions.LEFT:
            dx = -(min(self.offset, self.bounds.left))
            dy = 0
        elif self.direction == Directions.RIGHT:
            dx = min(self.offset, settings.SCREEN_WIDTH - self.bounds.right)
            dy = 0
        elif self.direction == Directions.UP:
            dx = 0
            dy = -min(self.offset, self.bounds.top)
        elif self.direction == Directions.DOWN:
            dx = 0
            dy = (min(self.offset, settings.SCREEN_HEIGHT - self.bounds.bottom))
        else:
            return

        if not self.is_moving:
            return

        self.move(dx, dy)
