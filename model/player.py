from model.constants import Directions
from model.game_object import GameObject
from model.projectile import Projectile
import random
import pygame
import settings


class AbstractPlayer(GameObject):
    KEYS_TO_DIRECTIONS = {
        pygame.K_a: Directions.LEFT,
        pygame.K_w: Directions.UP,
        pygame.K_d: Directions.RIGHT,
        pygame.K_s: Directions.DOWN
    }
    ALL_KEYS = (
        pygame.K_a, pygame.K_w, pygame.K_d, pygame.K_s, pygame.K_SPACE,
    )

    def __init__(self, x, y, radius, color, offset, game_objects):
        self.offset = offset
        self.radius = radius
        self.diameter = 2 * radius
        super().__init__(x-radius, y-radius, self.diameter, self.diameter)
        self.color = color
        self.direction = Directions.UP
        self.move_stack = []
        self.projectile_speed = settings.PROJECTILE_SPEED
        self.game_objects = game_objects
        self.previous_shooting_time = None

    def handle_up(self, key):
        raise NotImplementedError

    def handle_down(self, key):
        raise NotImplementedError

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.bounds.center, self.radius)

    def is_moving(self):
        return len(self.move_stack) != 0

    def shoot(self):
        if self.is_on_recharge():
            return
        self.previous_shooting_time = pygame.time.get_ticks()
        projectile = Projectile(
            *self.bounds.center,
            settings.PROJECTILE_RADIUS, settings.PROJECTILE_COLOR,
            settings.PROJECTILE_SPEED,
            self.direction,
        )
        self.game_objects.append(projectile)

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

        if not self.is_moving():
            return

        self.move(dx, dy)

    def is_on_recharge(self):
        if (
            not self.previous_shooting_time
            or pygame.time.get_ticks() - self.previous_shooting_time > settings.PLAYER_WEAPON_RECHARGE
        ):
            return False
        return True


class ClientPlayer(AbstractPlayer):
    def handle_up(self, key):
        if key in self.KEYS_TO_DIRECTIONS.keys():
            direction = self.KEYS_TO_DIRECTIONS[key]
            if direction in self.move_stack:
                self.move_stack.remove(direction)

            if self.move_stack:
                self.direction = self.move_stack[-1]

    def handle_down(self, key):
        if key in self.KEYS_TO_DIRECTIONS.keys():
            direction = self.KEYS_TO_DIRECTIONS[key]
            if direction in self.move_stack:
                self.move_stack.remove(direction)
            self.move_stack.append(direction)
            self.direction = direction
        if key == pygame.K_SPACE:
            self.shoot()


class Opponent(ClientPlayer):
    def __init__(self, x, y, radius, color, offset, game_objects):
        super().__init__(x, y, radius, color, offset, game_objects)
        self.current_key = None

    def handle_up(self, key):
        pass

    def handle_down(self, key):
        pass

    def is_changing_direction(self):
        if self.offset in (
            -self.bounds.left,
            settings.SCREEN_WIDTH - self.bounds.right,
            -self.bounds.top,
            settings.SCREEN_HEIGHT-self.bounds.bottom
        ):
            return True
        return not bool(random.randint(0, 20))

    def is_shooting(self):
        return not bool(random.randint(0, 40))

    def update(self):
        if self.is_shooting():
            super().shoot()
        if self.is_changing_direction():
            super().handle_up(self.current_key)
            self.current_key = random.choice(tuple(self.KEYS_TO_DIRECTIONS))
        super().handle_down(self.current_key)
        super().update()
