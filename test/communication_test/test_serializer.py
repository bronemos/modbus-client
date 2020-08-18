import pytest

from modbus_client.communication.serializer import *

protocol_code = '0000'


@pytest.mark.parametrize(['message', 'expected'],
                         [(bytes.fromhex('0005000000050201028002'), {'transaction_id': 5,
                                                                     'unit_address': 2,
                                                                     'function_code': 1,
                                                                     'status_list': [0, 0, 0, 0, 0, 0, 0, 1,
                                                                                     0, 1, 0, 0, 0, 0, 0, 0],
                                                                     'raw_data': bytes.fromhex('028002')}),
                          (bytes.fromhex('000A000000050102020500'), {'transaction_id': 10,
                                                                     'unit_address': 1,
                                                                     'function_code': 2,
                                                                     'status_list': [1, 0, 1, 0, 0, 0, 0, 0,
                                                                                     0, 0, 0, 0, 0, 0, 0, 0],
                                                                     'raw_data': bytes.fromhex('020500')}),
                          (bytes.fromhex('000F0000000701030403E81388'), {'transaction_id': 15,
                                                                         'unit_address': 1,
                                                                         'function_code': 3,
                                                                         'register_data': ['1000', '5000'],
                                                                         'raw_data': bytes.fromhex('0403E81388')}),
                          (bytes.fromhex('0014000000070104042710C350'), {'transaction_id': 20,
                                                                         'unit_address': 1,
                                                                         'function_code': 4,
                                                                         'register_data': ['10000', '50000'],
                                                                         'raw_data': bytes.fromhex('042710C350')}),
                          (bytes.fromhex('00190000000601050064FF00'), {'transaction_id': 25,
                                                                       'unit_address': 1,
                                                                       'function_code': 5,
                                                                       'raw_data': bytes.fromhex('0064FF00')}),
                          (bytes.fromhex('001E00000006010600643A98'), {'transaction_id': 30,
                                                                       'unit_address': 1,
                                                                       'function_code': 6,
                                                                       'raw_data': bytes.fromhex('00643A98')}),
                          (bytes.fromhex('0023000000061C1000640002'), {'transaction_id': 35,
                                                                       'unit_address': 28,
                                                                       'function_code': 16,
                                                                       'raw_data': bytes.fromhex('00640002')})])
def test_deserialize_message(message, expected):
    assert deserialize_message(message) == expected


@pytest.mark.parametrize(['function_code', 'transaction_id', 'unit_address', 'first_address', 'count', 'expected'],
                         [(1, 5, 2, 32, 12, '00050000000602010020000c'),
                          (2, 10, 1, 500, 32, '000a00000006010201f40020'),
                          (3, 15, 1, 600, 2, '000f00000006010302580002'),
                          (4, 20, 1, 200, 2, '001400000006010400c80002')])
def test_serialize_read(function_code, transaction_id, unit_address, first_address, count, expected):
    assert serialize_read(function_code, transaction_id, unit_address, first_address, count) == expected


@pytest.mark.parametrize(['transaction_id', 'unit_address', 'address', 'status', 'expected'],
                         [(25, 1, 100, True, '00190000000601050064FF00')])
def test_serialize_write_single_coil(transaction_id, unit_address, address, status, expected):
    assert serialize_write_single_coil(transaction_id, unit_address, address, status) == expected


@pytest.mark.parametrize(['transaction_id', 'unit_address', 'address', 'data', 'expected'],
                         [(30, 1, 100, 15000, '001e00000006010600643a98')])
def test_serialize_write_single_register(transaction_id, unit_address, address, data, expected):
    assert serialize_write_single_register(transaction_id, unit_address, address, data) == expected


@pytest.mark.parametrize(['transaction_id', 'unit_address', 'first_address', 'data', 'expected'],
                         [(1, 1, 19, ['1', '0', '1', '1', '0', '0', '1', '1', '1', '0'],
                           '000100000009010f0013000a02cd01')])
def test_serialize_write_multiple_coils(transaction_id, unit_address, first_address, data, expected):
    assert serialize_write_multiple_coils(transaction_id, unit_address, first_address, data) == expected


@pytest.mark.parametrize(['transaction_id', 'unit_address', 'first_address', 'data', 'expected'],
                         [(35, 28, 100, [1000, 2008], '00230000000b1c10006400020403e807d8')])
def test_serialize_write_multiple_registers(transaction_id, unit_address, first_address, data, expected):
    assert serialize_write_multiple_registers(transaction_id, unit_address, first_address, data) == expected
