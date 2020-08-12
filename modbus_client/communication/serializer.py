import math
from typing import Union

from modbus_client.resources.codes import Codes

protocol_code = '0000'


def deserialize_message(message: Union[str, bytes]) -> Union[str, dict]:
    """
    Function for deserializing messages of type string or bytes.

    Args:
        message (str, bytes): Message to be deserialized, can be either string or bytes.

    Returns:
        If the message is string, string format of the message is returned, otherwise a corresponding dictionary is created.
    """
    if type(message) == bytes:
        transaction_id = int(message[0:2].hex(), 16)
        unit_address = message[6]
        function_code = message[7]
        message_hex = message[9:].hex()
        raw_data = message[8:]
        if function_code == Codes.READ_COILS.value or function_code == Codes.READ_DISCRETE_INPUTS.value:
            status_list = [int(x) for x in ''.join([z[::-1] for z in
                                                    ['{:08b}'.format(int((x + y), 16)) for x, y in
                                                     zip(message_hex[::2], message_hex[1::2])]])]
            return {'transaction_id': transaction_id,
                    'unit_address': unit_address,
                    'function_code': function_code,
                    'status_list': status_list,
                    'raw_data': raw_data}
        elif function_code == Codes.READ_HOLDING_REGISTERS.value or function_code == Codes.READ_INPUT_REGISTERS.value:
            data_list = list()
            data_list.extend(
                [str(int(''.join(message_hex[i:i + 4]), 16)) for i in range(0, len(message_hex), 4)])
            return {'transaction_id': transaction_id,
                    'unit_address': unit_address,
                    'function_code': function_code,
                    'register_data': data_list,
                    'raw_data': raw_data}
        else:
            return {'transaction_id': transaction_id,
                    'unit_address': unit_address,
                    'function_code': function_code,
                    'raw_data': raw_data}

    else:
        print(message)
    return message


def serialize_read(function_code: int, transaction_id: int, unit_address: int, first_address: int, count: int) -> str:
    """
    Universal function for handling serialization of all read type messages.

    Args:
        function_code (int): Unique function code.
        transaction_id (int): Unique ID of the transaction.
        unit_address (int): Address of the referenced unit.
        first_address (int): Starting address.
        count (int): Number of items to be read.

    Returns:
        hex_string (str): Returns hex representation of the message in string format.

    """
    unit_address_hex = '{:02x}'.format(unit_address)
    function_code_hex = '{:02x}'.format(function_code)
    transaction_id_hex = '{:04x}'.format(transaction_id)
    first_address_hex = '{:04x}'.format(first_address)
    count_hex = '{:04x}'.format(count)
    length_hex = '0006'
    return (transaction_id_hex
            + protocol_code
            + length_hex
            + unit_address_hex
            + function_code_hex
            + first_address_hex
            + count_hex)


def serialize_write_single_coil(transaction_id: int, unit_address: int, address: int, status: bool) -> str:
    """
    Serializer function for writing single coil.

    Args:
        transaction_id: Unique ID of the transaction.
        unit_address (int): Address of the referenced unit.
        address (int): Address to be written to.
        status (bool): Status of the coil (True if set False otherwise)

    Returns:
        hex_string (str): Returns hex representation of the message in string format.
    """
    unit_address_hex = '{:02x}'.format(unit_address)
    function_code_hex = '{:02x}'.format(Codes.WRITE_SINGLE_COIL.value)
    transaction_id_hex = '{:04x}'.format(transaction_id)
    address_hex = '{:04x}'.format(address)
    status_hex = 'FF00' if status else '0000'
    length_hex = '0006'
    return (transaction_id_hex
            + protocol_code
            + length_hex
            + unit_address_hex
            + function_code_hex
            + address_hex
            + status_hex)


def serialize_write_single_register(transaction_id: int, unit_address: int, address: int, data: int) -> str:
    """
    Serializer function for writing to a single register.

    Args:
        transaction_id (int): Unique ID of the transaction.
        unit_address (int): Address of the referenced unit.
        address (int): Address to be written to.
        data (int): Data to be written in the register.

    Returns:
        hex_string (str): Returns hex representation of the message in string format.
    """
    unit_address_hex = '{:02x}'.format(unit_address)
    function_code_hex = '{:02x}'.format(Codes.WRITE_SINGLE_REGISTER.value)
    transaction_id_hex = '{:04x}'.format(transaction_id)
    address_hex = '{:04x}'.format(address)
    data_hex = '{:04x}'.format(data)
    length_hex = '0006'
    return (transaction_id_hex
            + protocol_code
            + length_hex
            + unit_address_hex
            + function_code_hex
            + address_hex
            + data_hex)


def serialize_write_multiple_coils(transaction_id: int, unit_address: int, first_address: int, data: list) -> str:
    """
    Serializer function for writing multiple coils.

    Args:
        transaction_id (int): Unique ID of the transaction.
        unit_address (int): Address of the referenced unit.
        first_address (int): Starting address.
        data (list): List of data to be written.

    Returns:
        hex_string (str): Returns hex representation of the message in string format.
    """
    unit_address_hex = '{:02x}'.format(unit_address)
    function_code_hex = '{:02x}'.format(Codes.WRITE_MULTIPLE_COILS.value)
    transaction_id_hex = '{:04x}'.format(transaction_id)
    first_address_hex = '{:04x}'.format(first_address)
    length_hex = '{:04x}'.format(1 + 1 + 2 + 2 + 1 + math.ceil(len(data) / 8))
    data_hex = ''.join(['{:02x}'.format(int(''.join(z), 2)) for z in
                        [x[::-1] for x in [data[i:i + 8] for i in range(0, len(data), 8)]]])
    coil_count_hex = '{:04x}'.format(len(data))
    byte_count_hex = '{:02x}'.format(math.ceil(len(data) / 8))
    return (transaction_id_hex
            + protocol_code
            + length_hex
            + unit_address_hex
            + function_code_hex
            + first_address_hex
            + coil_count_hex
            + byte_count_hex
            + data_hex)


def serialize_write_multiple_registers(transaction_id: int, unit_address: int, first_address: int, data: list) -> str:
    """
    Serializer function for writing multiple registers.

    Args:
        transaction_id (int): Unique ID of the transaction.
        unit_address (int): Address of the referenced unit.
        first_address (int): Starting address.
        data (list): List of data to be written.

    Returns:
        hex_string (str): Returns hex representation of the message in string format.
    """
    unit_address_hex = '{:02x}'.format(unit_address)
    function_code_hex = '{:02x}'.format(Codes.WRITE_MULTIPLE_REGISTERS.value)
    transaction_id_hex = '{:04x}'.format(transaction_id)
    first_address_hex = '{:04x}'.format(first_address)
    length_hex = '{:04x}'.format(1 + 1 + 2 + 2 + 1 + 2 * len(data))
    data_hex = ''.join(['{:04x}'.format(x) for x in data])
    register_count_hex = '{:04x}'.format(len(data))
    byte_count_hex = '{:02x}'.format(2 * len(data))
    return (transaction_id_hex
            + protocol_code
            + length_hex
            + unit_address_hex
            + function_code_hex
            + first_address_hex
            + register_count_hex
            + byte_count_hex
            + data_hex)
