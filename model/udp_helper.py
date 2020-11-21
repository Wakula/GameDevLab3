from udp_communication.messages import messages_pb2
from model.projectile import Projectile
from model.boost_mappings import BOOST_CLS_TO_BOOST_TYPE, BOOST_TYPE_TO_BOOST_CLS
from model import constants
import settings


def create_boost(boost_message):
    boost_cls = BOOST_TYPE_TO_BOOST_CLS[boost_message.type]
    return boost_cls(
        boost_id=boost_message.boost_id,
        x=boost_message.x,
        y=boost_message.y,
        w=settings.BOOST_WIDTH,
        h=settings.BOOST_HEIGHT,
    )


def create_boost_message(boost):
    boost_message = messages_pb2.Boost()
    boost_message.type = BOOST_CLS_TO_BOOST_TYPE[type(boost)]
    boost_message.boost_id = boost.boost_id
    boost_message.x = boost.bounds.x
    boost_message.y = boost.bounds.y
    return boost_message


def create_boost_pick_up_message(boost):
    boost_pick_up = messages_pb2.BoostPickUp()
    boost_pick_up.player_id = boost.player.player_id
    boost_pick_up.boost_id = boost.boost_id
    return boost_pick_up


def create_dead_player_state(player_id):
    player_state = messages_pb2.PlayerIsDead()
    player_state.player_id = player_id
    return player_state


def create_player_state(player):
    player_state = messages_pb2.PlayerState()
    player_state.player_id = player.player_id
    player_state.x = player.bounds.x
    player_state.y = player.bounds.y
    player_state.direction = player.direction.value
    player_state.health = player.health
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
