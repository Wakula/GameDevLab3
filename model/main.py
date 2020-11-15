from collections import defaultdict
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
    PLAYER_KEYS = (
        pygame.K_a,
        pygame.K_w,
        pygame.K_d,
        pygame.K_s,
    )

    def __init__(self, x, y, radius, color, offset):
        self.offset = offset
        self.radius = radius
        self.diameter = 2 * radius
        super().__init__(x-radius, y-radius, self.diameter, self.diameter)
        # TODO: should also display direction
        self.color = color
        self.moving_left = False
        self.moving_up = False
        self.moving_right = False
        self.moving_down = False

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.bounds.center, self.radius)

    def handle(self, key):
        if key == pygame.K_a:
            self.moving_left = not self.moving_left
        elif key == pygame.K_w:
            self.moving_up = not self.moving_up
        elif key == pygame.K_s:
            self.moving_down = not self.moving_down
        elif key == pygame.K_d:
            self.moving_right = not self.moving_right

    def update(self):
        if self.moving_left:
            dx = -(min(self.offset, self.bounds.left))
            dy = 0
        elif self.moving_right:
            dx = min(self.offset, settings.SCREEN_WIDTH - self.bounds.right)
            dy = 0
        elif self.moving_up:
            dx = 0
            dy = -min(self.offset, self.bounds.top)
        elif self.moving_down:
            dx = 0
            dy = (min(self.offset, settings.SCREEN_HEIGHT - self.bounds.bottom))
        else:
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
        for key in player.PLAYER_KEYS:
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
