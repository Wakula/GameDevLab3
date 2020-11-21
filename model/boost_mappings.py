from udp_communication.messages.messages_pb2 import Boost
from model.boosts import HealthBoost, PlayerDamageBoost, PlayerSpeedBoost, ProjectileSpeedBoost

BOOST_CLS_TO_BOOST_TYPE = {
    HealthBoost: Boost.Type.HEALTH,
    PlayerDamageBoost: Boost.Type.PLAYER_DAMAGE,
    PlayerSpeedBoost: Boost.Type.PLAYER_SPEED,
    ProjectileSpeedBoost: Boost.Type.PROJECTILE_SPEED,
}

BOOST_TYPE_TO_BOOST_CLS = {
    type_: boost_cls for boost_cls, type_ in BOOST_CLS_TO_BOOST_TYPE.items()
}
