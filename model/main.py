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


class Game:
    def __init__(self):
        self.game_over = False
        self.objects = []
        pygame.init()
        self.surface = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.key_down_handlers = defaultdict(list)
        self.key_up_handlers = defaultdict(list)
        # TODO: this should be changed for multiple players
        self._init_player()

    def _init_player(self):
        # TODO: x_... and y_... spawn position should be reworked
        x_spawn_position = int((settings.SCREEN_WIDTH - settings.PLAYER_RADIUS) / 2)
        y_spawn_position = settings.SCREEN_HEIGHT - settings.PLAYER_RADIUS * 2
        player = Player(
            x_spawn_position,
            y_spawn_position,
            settings.PLAYER_RADIUS,
            settings.PLAYER_COLOR,
            settings.PLAYER_SPEED,
        )
        for key in player.KEYS_TO_DIRECTIONS.keys():
            self.key_down_handlers[key].append(player.handle)
            self.key_up_handlers[key].append(player.handle)

        self.objects.append(player)

    def update(self):
        for game_object in self.objects:
            game_object.update()

    def draw(self):
        for game_object in self.objects:
            game_object.draw(self.surface)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                
            if event.type == pygame.KEYDOWN:
                for handler in self.key_down_handlers[event.key]:
                    handler(event.key)
            elif event.type == pygame.KEYUP:
                for handler in self.key_up_handlers[event.key]:
                    handler(event.key)

    def run(self):
        while not self.game_over:
            self.surface.fill(settings.BACKGROUND_COLOR)
            self.handle_events()
            self.update()
            self.draw()

            pygame.display.update()
            self.clock.tick(settings.FRAME_RATE)
