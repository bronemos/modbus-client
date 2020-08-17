import math
from typing import Union

import pytest

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


@pytest.mark.parametrize(['function_code', 'transaction_id', 'unit_address', 'first_address', 'count', 'expected'],
                         [(1, 5, 2, 32, 12, '00050000000602010020000c'),
                          (2, 10, 1, 500, 32, '000a00000006010201f40020'),
                          (3, 15, 1, 600, 2, '000f00000006010302580002'),
                          (4, 20, 1, 200, 2, '001400000006010400c80002')])
def test_serialize_read(function_code, transaction_id, unit_address, first_address, count, expected):
    assert serialize_read(function_code, transaction_id, unit_address, first_address, count) == expected


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
        hex_string (str): Hex representation of the message in string format.

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


@pytest.mark.parametrize(['transaction_id', 'unit_address', 'address', 'status', 'expected'],
                         [(25, 1, 100, True, '00190000000601050064FF00')])
def test_serialize_write_single_coil(transaction_id, unit_address, address, status, expected):
    assert serialize_write_single_coil(transaction_id, unit_address, address, status) == expected


def serialize_write_single_coil(transaction_id: int, unit_address: int, address: int, status: bool) -> str:
    """
    Serializer function for writing single coil.

    Args:
        transaction_id: Unique ID of the transaction.
        unit_address (int): Address of the referenced unit.
        address (int): Address to be written to.
        status (bool): Status of the coil (True if set False otherwise)

    Returns:
        hex_string (str): Hex representation of the message in string format.
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


@pytest.mark.parametrize(['transaction_id', 'unit_address', 'address', 'data', 'expected'],
                         [(30, 1, 100, 15000, '001e00000006010600643a98')])
def test_serialize_write_single_register(transaction_id, unit_address, address, data, expected):
    assert serialize_write_single_register(transaction_id, unit_address, address, data) == expected


def serialize_write_single_register(transaction_id: int, unit_address: int, address: int, data: int) -> str:
    """
    Serializer function for writing to a single register.

    Args:
        transaction_id (int): Unique ID of the transaction.
        unit_address (int): Address of the referenced unit.
        address (int): Address to be written to.
        data (int): Data to be written in the register.

    Returns:
        hex_string (str): Hex representation of the message in string format.
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


@pytest.mark.parametrize(['transaction_id', 'unit_address', 'first_address', 'data', 'expected'],
                         [(1, 1, 19, '1011001110', '000100000009010f0013000a02cd01')])
def test_serialize_write_multiple_coils(transaction_id, unit_address, first_address, data, expected):
    assert serialize_write_multiple_coils(transaction_id, unit_address, first_address, data) == expected


def serialize_write_multiple_coils(transaction_id: int, unit_address: int, first_address: int, data: list) -> str:
    """
    Serializer function for writing multiple coils.

    Args:
        transaction_id (int): Unique ID of the transaction.
        unit_address (int): Address of the referenced unit.
        first_address (int): Starting address.
        data (list): List of data to be written.

    Returns:
        hex_string (str): Hex representation of the message in string format.
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


@pytest.mark.parametrize(['transaction_id', 'unit_address', 'first_address', 'data', 'expected'],
                         [(35, 28, 100, [1000, 2008], '00230000000b1c10006400020403e807d8')])
def test_serialize_write_multiple_registers(transaction_id, unit_address, first_address, data, expected):
    assert serialize_write_multiple_registers(transaction_id, unit_address, first_address, data) == expected


def serialize_write_multiple_registers(transaction_id: int, unit_address: int, first_address: int, data: list) -> str:
    """
    Serializer function for writing multiple registers.

    Args:
        transaction_id (int): Unique ID of the transaction.
        unit_address (int): Address of the referenced unit.
        first_address (int): Starting address.
        data (list): List of data to be written.

    Returns:
        hex_string (str): Hex representation of the message in string format.
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
