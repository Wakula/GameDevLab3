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
        pygame.font.init()
        self.game_font = pygame.font.SysFont(settings.FONT, settings.FONT_SIZE)

    def init_client_player(self, x_spawn, y_spawn, player_dir, player_id):
        # TODO: x_... and y_... spawn position should be reworked
        player = ClientPlayer(
            x_spawn,
            y_spawn,
            settings.PLAYER_RADIUS,
            settings.PLAYER_COLOR,
            settings.PLAYER_SPEED,
            self,
            player_id
        )
        player.direction = player_dir
        for key in player.ALL_KEYS:
            self.key_down_handlers[key].append(player.handle_down)
            self.key_up_handlers[key].append(player.handle_up)

        self.players[player_id] = player

    def init_ai_opponent(self, x_spawn, y_spawn):
        ai_id = "ai"
        opponent = Opponent(
            x_spawn,
            y_spawn,
            settings.PLAYER_RADIUS,
            settings.OPPONENT_COLOR,
            settings.PLAYER_SPEED,
            self,
            ai_id
        )
        self.players[ai_id] = player
    
    def init_network_opponent(self, x_spawn, y_spawn, player_dir, player_id):
        opponent = NetworkOpponent(
            x_spawn,
            y_spawn,
            settings.PLAYER_RADIUS,
            settings.OPPONENT_COLOR,
            settings.PLAYER_SPEED,
            self,
            player_id
        )
        opponent.direction = player_dir
        self.players[player_id] = opponent

    def update(self):
        for game_object in self.objects:
            game_object.update()
        self.handle_projectile_collisions()
        self.handle_boosts_collisions()
        self.try_undo_boosts_effects()
        self.spawn_boosts()

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

    def handle_start(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return True

        return False

    def show_start_screen(self):
        self.clean_screen()
        self.render_text(settings.START_SCREEN_TEXT)
        pygame.display.update()
        while not self.handle_start():
            pass

    def show_end_screen(self, is_client_winner):
        self.clean_screen()
        text = settings.WINNER_TEXT if is_client_winner else settings.GAME_OVER_TEXT
        self.render_text(text)
        pygame.display.update()
        while not self.handle_start():
            pass
    
    def show_connecting(self):
        self.clean_screen()
        self.render_text(settings.CONNECTING_TEXT)
        pygame.display.update()

    def render_text(self, text):
        textsurface = self.game_font.render(text, False, settings.FONT_COLOR)
        rect = textsurface.get_rect()
        center_x = settings.SCREEN_WIDTH / 2 - rect.width / 2
        center_y = settings.SCREEN_HEIGHT / 2 - rect.height / 2
        self.surface.blit(textsurface, (center_x, center_y))

    def clean_screen(self):
        self.surface.fill(settings.BACKGROUND_COLOR)

    def run(self):
        self.clean_screen()
        self.handle_events()
        self.update()
        self.draw()
        pygame.display.update()
        self.clock.tick(settings.FRAME_RATE)
