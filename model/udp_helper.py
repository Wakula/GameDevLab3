from udp_communication.messages import messages_pb2
from model.projectile import Projectile
from model import constants
import settings


def create_player_state(player):
    player_state = messages_pb2.PlayerState()
    player_state.player_id = player.player_id
    player_state.x = player.bounds.x
    player_state.y = player.bounds.y
    player_state.direction = player.direction.value
    return player_state


def create_shoot_event(projectile):
    shoot_event = messages_pb2.ShootEvent()
    shoot_event.projectile_id = projectile.id[1]
    shoot_event.x, shoot_event.y = projectile.bounds.center
    shoot_event.damage = projectile.damage
    shoot_event.direction = projectile.owner.direction.value
    shoot_event.speed = projectile.owner.projectile_speed
    shoot_event.player_id = projectile.owner.player_id
    return shoot_event


def create_projectile(shoot_event, owner):
    owner.direction = constants.Directions(shoot_event.direction)
    return Projectile(
        x=shoot_event.x,
        y=shoot_event.y,
        radius=settings.PROJECTILE_RADIUS,
        color=settings.PROJECTILE_COLOR,
        owner=owner,
        damage=shoot_event.damage,
        speed=shoot_event.speed,
    )
