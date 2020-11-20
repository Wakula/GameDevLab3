from udp_communication.messages.messages_pb2 import PlayerState

def create_player_state(player):
    playerState = PlayerState()
    playerState.player_id = player.player_id 
    playerState.x = player.bounds.x 
    playerState.y = player.bounds.y 
    playerState.direction = player.direction.value
    return playerState