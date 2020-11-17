from udp_communication.messages import messages_pb2

CODES_TO_MESSAGES = (
    messages_pb2.Connect,
    messages_pb2.GameStarted,
    messages_pb2.GameStartedOk,
    messages_pb2.PlayerState,
    messages_pb2.GameState,
)

MESSAGES_TO_CODES = {
    CODES_TO_MESSAGES[code]: code for code in range(len(CODES_TO_MESSAGES))
}

MESSAGE_TO_APPROVAL = {
    messages_pb2.Connect: messages_pb2.GameStarted,
    messages_pb2.GameStarted: messages_pb2.GameStartedOk,
    messages_pb2.GameStartedOk: messages_pb2.GameState,
}