from collections import defaultdict
from model.constants import Directions
import pygame
import settings


class GameObject:
    def __init__(self, x, y, w, h, speed=(0, 0)):
        self.bounds = pygame.Rect(x, y, w, h)
        self.speed = speed

    def draw(self, surface):
        raise NotImplementedError

    def move(self, dx, dy):
        self.bounds = self.bounds.move(dx, dy)

    def update(self):
        if self.speed == (0, 0):
            return

        self.move(*self.speed)
