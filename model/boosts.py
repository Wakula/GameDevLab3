import settings
from model.game_object import GameObject
import pygame


class AbstractBoost(GameObject):
    COLOR = None

    def __init__(self, x, y, w, h):
        self.player = None
        super().__init__(x, y, w, h)

    def draw(self, surface):
        pygame.draw.rect(surface, self.COLOR, self.bounds)

    def attach_to_player(self, player):
        self.player = player

    def is_effect_undone(self):
        return not self.player

    def apply_effect(self):
        raise NotImplementedError

    def try_undo_effect(self):
        self.player = None


class HealthBoost(AbstractBoost):
    COLOR = settings.HEALTH_BOOST_COLOR

    def apply_effect(self):
        if self.player.health == settings.MAX_HEALTH:
            return
        updated_health = self.player.health + settings.HEALTH_BOOST_EFFECT
        if updated_health > settings.MAX_HEALTH:
            self.player.health = settings.MAX_HEALTH


class AbstractMultiplierBoostWithDuration(AbstractBoost):
    DURATION = settings.BASE_BOOSTS_DURATION
    VALUE_TO_BOOST = None
    BOOST_MULTIPLIER = None

    def __init__(self, x, y, w, h):
        self.effect_started = None
        super().__init__(x, y, w, h)

    def get_boosted_value(self):
        return self.VALUE_TO_BOOST * self.BOOST_MULTIPLIER

    def apply_effect(self):
        boosted_value = self.get_boosted_value()
        if self.get_player_value() == boosted_value:
            self.player = None
            return
        self.effect_started = pygame.time.get_ticks()
        self.set_value(boosted_value)

    def try_undo_effect(self):
        if self.player is None or pygame.time.get_ticks() - self.effect_started < self.DURATION:
            return
        self.set_value(self.VALUE_TO_BOOST)
        super().try_undo_effect()

    def set_value(self, value):
        raise NotImplementedError

    def get_player_value(self):
        raise NotImplementedError


class ProjectileSpeedBoost(AbstractMultiplierBoostWithDuration):
    COLOR = settings.PROJECTILE_SPEED_BOOST_COLOR
    VALUE_TO_BOOST = settings.PROJECTILE_SPEED
    BOOST_MULTIPLIER = settings.PROJECTILE_SPEED_BOOST_MULTIPLIER

    def set_value(self, value):
        self.player.projectile_speed = value

    def get_player_value(self):
        return self.player.projectile_speed


class PlayerSpeedBoost(AbstractMultiplierBoostWithDuration):
    COLOR = settings.PLAYER_SPEED_BOOST_COLOR
    VALUE_TO_BOOST = settings.PLAYER_SPEED
    BOOST_MULTIPLIER = settings.PLAYER_SPEED_BOOST_MULTIPLIER

    def set_value(self, value):
        self.player.offset = value

    def get_player_value(self):
        return self.player.offset


class PlayerDamageBoost(AbstractMultiplierBoostWithDuration):
    COLOR = settings.PLAYER_DAMAGE_BOOST_COLOR
    VALUE_TO_BOOST = settings.PROJECTILE_BASE_DAMAGE
    BOOST_MULTIPLIER = settings.PLAYER_DAMAGE_BOOST_MULTIPLIER

    def set_value(self, value):
        self.player.projectile_damage = value

    def get_player_value(self):
        return self.player.projectile_damage
