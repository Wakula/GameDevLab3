from collections import defaultdict
from socket import timeout
import socket
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
    def __init__(self, host, read_port=0):
        read_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        read_sock.settimeout(0.1)
        write_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        read_sock.bind((host, read_port))
        write_sock.bind((host, 0))
        self.read_socket = read_sock
        self.write_socket = write_sock
        self.message_id = 1
        self.message_to_read = None

    def send_approval_message_on(self, message):
        pass

    def read(self):
        address_to_messages = defaultdict(dict)
        for _ in range(20):
            try:
                message, address = self._read()
            except timeout:
                break
            code = MESSAGES_TO_CODES[type(message)]
            previous_message = address_to_messages[address].get(code)
            if not previous_message or message.message_id > previous_message.message_id:
                address_to_messages[address][code] = message
        return {address: tuple(messages.values()) for address, messages in address_to_messages.items()}

    def _read(self):
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
        return message, address

    def send(self, message, host, port):
        self._send(message, host, port)
        self.message_id += 1

    def send_until_approval(self, message, host, port):
        # TODO: deal with lost messages
        # TODO: handle cases when not responding for too long
        address = None
        while True:
            for _ in range(REPEATED_MESSAGES_AMOUNT):
                self._send(message, host, port)
            while address != (host, port):
                approval_message, address = self._read()
            address = None
            if is_required_approval_message(message, approval_message):
                self.message_id += 1
                return approval_message

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
