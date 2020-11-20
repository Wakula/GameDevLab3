from udp_communication.constants import (
    BYTEORDER_FOR_MESSAGE_CODE, BYTES_FOR_MESSAGE_CODE, MAX_MESSAGE_LEN, REPEATED_MESSAGES_AMOUNT,
)
from udp_communication.messages.codes import CODES_TO_MESSAGES, MESSAGES_TO_CODES, MESSAGE_TO_APPROVAL
import settings


def is_required_approval_message(message, approval_message):
    required_message_type = MESSAGE_TO_APPROVAL[type(message)]
    return isinstance(approval_message, required_message_type)


def encode_address(host, port):
    # 6 bytes total
    encoded_host = b''.join(int(num).to_bytes(1, BYTEORDER_FOR_MESSAGE_CODE) for num in host.split('.'))
    encoded_port = port.to_bytes(2, BYTEORDER_FOR_MESSAGE_CODE)
    return encoded_host + encoded_port


def decode_address(encoded_address):
    encoded_host = encoded_address[:4]
    encoded_port = encoded_address[4:]
    decoded_host = '.'.join(str(byte) for byte in encoded_host)
    decoded_port = int.from_bytes(encoded_port, BYTEORDER_FOR_MESSAGE_CODE)
    return decoded_host, decoded_port


class UDPCommunicator:
    def __init__(self, read_socket, write_socket):
        self.read_socket = read_socket
        self.write_socket = write_socket
        self.message_id = 1
        self.message_to_read = None

    def send_approval_message_on(self, message):
        pass

    def read(self):
        if self.message_to_read:
            return self.message_to_read
        encoded_message = self.read_socket.recv(MAX_MESSAGE_LEN)
        sender_address_bytes = encoded_message[:6]
        message_code_bytes = encoded_message[6:6+BYTES_FOR_MESSAGE_CODE]
        message_bytes = encoded_message[6+BYTES_FOR_MESSAGE_CODE:]
        # TODO: handle if cant parse message_code, or no message with given code
        message_code = int.from_bytes(message_code_bytes, BYTEORDER_FOR_MESSAGE_CODE)
        message_cls = CODES_TO_MESSAGES[message_code]
        message = message_cls()
        message.ParseFromString(message_bytes)
        address = decode_address(sender_address_bytes)
        print("im reading")
        print(type(message), address)
        return message, address

    def send(self, message, host, port):
        # TODO: handle message.message_id
        self._send(message, host, port)

    def send_until_approval(self, message, host, port):
        # TODO: deal with lost messages
        # TODO: handle cases when not responding for too long
        approved = False
        address = None
        while not approved:
            for _ in range(REPEATED_MESSAGES_AMOUNT):
                self._send(message, host, port)
            while address != (host, port):
                approval_message, address = self.read()
            address = None
            if is_required_approval_message(message, approval_message):
                approved = True
                return approval_message

    def _send(self, message, host, port):
        sender_host, sender_port = self.read_socket.getsockname()
        sender_address_bytes = encode_address(sender_host, sender_port)
        message.message_id = self.message_id
        message_code = MESSAGES_TO_CODES[type(message)]
        message_code_bytes = message_code.to_bytes(BYTES_FOR_MESSAGE_CODE, BYTEORDER_FOR_MESSAGE_CODE)
        message_bytes = message.SerializeToString()
        # TODO: handle if message len is too long
        encoded_message = sender_address_bytes + message_code_bytes + message_bytes
        self.write_socket.sendto(encoded_message, (host, port))
