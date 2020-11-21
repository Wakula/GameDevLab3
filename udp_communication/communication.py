from collections import defaultdict
from udp_communication import constants
from socket import timeout
import socket
import settings
from udp_communication.constants import (
    BYTEORDER_FOR_MESSAGE_CODE, BYTES_FOR_MESSAGE_CODE, MAX_MESSAGE_LEN
)
from udp_communication.messages.codes import (
    CODES_TO_MESSAGES, MESSAGES_TO_CODES,
    MESSAGE_TO_ID_APPROVAL, MESSAGE_TO_MESSAGE_APPROVAL
)


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
    def __init__(self, host, read_port=0, is_client=False):
        read_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        read_sock.settimeout(constants.SOCKET_TIMEOUT)
        write_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        read_sock.bind((host, read_port))
        write_sock.bind((host, 0))
        self.read_socket = read_sock
        self.write_socket = write_sock
        self.message_id = 1
        self.is_client = is_client
        self.last_approval_message_id = None
        self.unfinished_approvals = []

    def is_required_approval_message(self, message, approval_message):
        if type(message) in MESSAGE_TO_ID_APPROVAL:
            return approval_message.message_id > self.last_approval_message_id
        required_message_type = MESSAGE_TO_MESSAGE_APPROVAL[type(message)]
        return isinstance(approval_message, required_message_type)

    def read(self):
        address_to_messages = defaultdict(dict)
        for _ in range(constants.MESSAGES_PER_READ):
            if not self.is_client and len(address_to_messages) >= settings.CLIENTS_AMOUNT:
                break
            try:
                message, address = self._read()
            except timeout:
                break
            message_type = type(message)
            messages = address_to_messages[address].get(message_type, {})
            messages[message.message_id] = message
            address_to_messages[address][message_type] = messages
        return {
            address: {message_type: tuple(messages.values()) for message_type, messages in type_to_messages.items()}
            for address, type_to_messages in address_to_messages.items()
        }

    def _read(self):
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
        return message, address

    def send_unfinished_approvals(self):
        if self.unfinished_approvals:
            unfinished_approvals = self.unfinished_approvals
            self.unfinished_approvals = []
            for approval in unfinished_approvals:
                message, host, port = approval
                message.message_id = self.message_id
                self.send_until_approval(message, host, port)

    def send(self, message, host, port):
        self.send_unfinished_approvals()
        self._send(message, host, port)
        self.message_id += 1

    def send_until_approval(self, message, host, port):
        self.send_unfinished_approvals()
        for _ in range(constants.APPROVAL_TRIES):
            self._send(message, host, port)
            try:
                approval_message, address = self._read()
            except timeout:
                continue
            if address == (host, port) and self.is_required_approval_message(message, approval_message):
                self.message_id += 1
                self.last_approval_message_id = approval_message.message_id
                return approval_message
        self.unfinished_approvals.append((message, host, port))

    def _send(self, message, host, port):
        message.message_id = self.message_id
        sender_host, sender_port = self.read_socket.getsockname()
        sender_address_bytes = encode_address(sender_host, sender_port)
        message_code = MESSAGES_TO_CODES[type(message)]
        message_code_bytes = message_code.to_bytes(BYTES_FOR_MESSAGE_CODE, BYTEORDER_FOR_MESSAGE_CODE)
        message_bytes = message.SerializeToString()
        # TODO: handle if message len is too long
        encoded_message = sender_address_bytes + message_code_bytes + message_bytes
        self.write_socket.sendto(encoded_message, (host, port))
