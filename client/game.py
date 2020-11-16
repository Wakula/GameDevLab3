from collections import defaultdict
from model.constants import Directions
from model.player import Player
import pygame
import settings


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
            self.objects,
        )
        for key in player.ALL_KEYS:
            self.key_down_handlers[key].append(player.handle_down)
            self.key_up_handlers[key].append(player.handle_up)

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
