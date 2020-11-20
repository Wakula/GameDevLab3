from model.constants import Directions, DIRECTIONS_TO_DELTA
from model.game_object import GameObject
from model.projectile import Projectile
import random
import pygame
import settings


class AbstractPlayer(GameObject):
    def __init__(self, x, y, radius, offset, game, player_id):
        self.offset = offset
        self.radius = radius
        self.diameter = 2 * radius
        self.direction = Directions.UP
        self.projectile_speed = settings.PROJECTILE_SPEED
        self.game = game
        self.previous_shooting_time = None
        self.health = settings.MAX_HEALTH
        self.player_id = player_id
        super().__init__(x-radius, y-radius, self.diameter, self.diameter)
        
    def shoot(self):
        if self.is_on_recharge():
            return
        self.previous_shooting_time = pygame.time.get_ticks()
        projectile = Projectile(
            *self.bounds.center,
            settings.PROJECTILE_RADIUS, settings.PROJECTILE_COLOR,
            settings.PROJECTILE_SPEED,
            self,
            settings.PROJECTILE_BASE_DAMAGE
        )
        self.game.projectiles.append(projectile)

    def is_on_recharge(self):
        if (
            not self.previous_shooting_time
            or self.game.get_ticks() - self.previous_shooting_time > settings.PLAYER_WEAPON_RECHARGE
        ):
            return False
        return True
