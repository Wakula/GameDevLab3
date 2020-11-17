from collections import defaultdict
from client.client_player import ClientPlayer, Opponent, NetworkOpponent
from model.game import AbstractGame
import pygame
import settings

class ClientGame(AbstractGame):
    def __init__(self):
        super().__init__()
        self.surface = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.key_down_handlers = defaultdict(list)
        self.key_up_handlers = defaultdict(list)
        # TODO: this should be changed for multiple players
        x_spawn_position = int((settings.SCREEN_WIDTH - settings.PLAYER_RADIUS) / 2)
        y_spawn_position = settings.SCREEN_HEIGHT - settings.PLAYER_RADIUS * 2
        self.init_client_player(x_spawn_position, y_spawn_position)
        self.init_ai_opponent(x_spawn_position, y_spawn_position)

    def init_client_player(self, x_spawn, y_spawn):
        # TODO: x_... and y_... spawn position should be reworked
        player = ClientPlayer(
            x_spawn,
            y_spawn,
            settings.PLAYER_RADIUS,
            settings.PLAYER_COLOR,
            settings.PLAYER_SPEED,
            self,
            "id1"
        )
        for key in player.ALL_KEYS:
            self.key_down_handlers[key].append(player.handle_down)
            self.key_up_handlers[key].append(player.handle_up)

        self.players.append(player)

    def init_ai_opponent(self, x_spawn, y_spawn):
        opponent = Opponent(
            x_spawn,
            y_spawn,
            settings.PLAYER_RADIUS,
            settings.OPPONENT_COLOR,
            settings.PLAYER_SPEED,
            self,
            "id2"
        )
        self.players.append(opponent)
    
    def init_network_opponent(self, x_spawn, y_spawn, player_id):
        opponent = NetworkOpponent(
            x_spawn,
            y_spawn,
            settings.PLAYER_RADIUS,
            settings.OPPONENT_COLOR,
            settings.PLAYER_SPEED,
            self,
            player_id
        )
        self.players.append(opponent)

    def update(self):
        for game_object in self.objects:
            game_object.update()
        self.handle_projectile_collisions()

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
    