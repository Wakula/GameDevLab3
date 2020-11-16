from collections import defaultdict
from model.player import ClientPlayer, Opponent
import pygame
import settings


class Game:
    def __init__(self):
        self.game_over = False
        self.players = []
        self.projectiles = []
        pygame.init()
        self.surface = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.key_down_handlers = defaultdict(list)
        self.key_up_handlers = defaultdict(list)
        # TODO: this should be changed for multiple players
        self._init_client_player()
        self._init_opponents()

    @property
    def objects(self):
        return (*self.players, *self.projectiles)

    def _init_client_player(self):
        # TODO: x_... and y_... spawn position should be reworked
        x_spawn_position = int((settings.SCREEN_WIDTH - settings.PLAYER_RADIUS) / 2)
        y_spawn_position = settings.SCREEN_HEIGHT - settings.PLAYER_RADIUS * 2
        player = ClientPlayer(
            x_spawn_position,
            y_spawn_position,
            settings.PLAYER_RADIUS,
            settings.PLAYER_COLOR,
            settings.PLAYER_SPEED,
            self.projectiles,
        )
        for key in player.ALL_KEYS:
            self.key_down_handlers[key].append(player.handle_down)
            self.key_up_handlers[key].append(player.handle_up)

        self.players.append(player)

    def _init_opponents(self):
        x_spawn_position = int((settings.SCREEN_WIDTH - settings.PLAYER_RADIUS) / 2)
        y_spawn_position = settings.SCREEN_HEIGHT - settings.PLAYER_RADIUS * 2
        opponent = Opponent(
            x_spawn_position,
            y_spawn_position,
            settings.PLAYER_RADIUS,
            settings.OPPONENT_COLOR,
            settings.PLAYER_SPEED,
            self.projectiles,
        )
        self.players.append(opponent)

    def handle_projectile_collisions(self):
        collided_projectiles = []
        dead_players = []
        for projectile in self.projectiles:
            for player in self.players:
                if player is projectile.owner:
                    continue
                if player.bounds.colliderect(projectile.bounds):
                    self.on_player_hit(projectile, player, dead_players)
                    collided_projectiles.append(projectile)
            if projectile not in collided_projectiles and projectile.is_out_of_bounds():
                collided_projectiles.append(projectile)
        self.remove_objects(collided_projectiles, dead_players)

    def on_player_hit(self, projectile, player, dead_players):
        projectile.hit(player)
        if player.health <= 0:
            dead_players.append(player)

    def remove_objects(self, collided_projectiles, dead_players):
        for projectile in collided_projectiles:
            self.projectiles.remove(projectile)
        for player in dead_players:
            self.players.remove(player)

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
