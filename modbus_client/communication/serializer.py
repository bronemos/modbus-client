import math

from modbus_client.resources.codes import Codes

protocol_code = '0000'


def deserialize_message(message):
    if type(message) == bytes:
        transaction_id = int(message[0:2].hex(), 16)
        unit_address = message[6]
        function_code = message[7]
        print(f'function code:{function_code}')
        message_hex = message[9:].hex()
        raw_data = message[8:]
        print('msg hex: ', message_hex)
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
            print(data_list)
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


def serialize_message(message):
    function_code = message['function_code']
    unit_address_hex = '{:02x}'.format(message['unit_address'])
    function_code_hex = '{:02x}'.format(function_code)
    transaction_id_hex = '{:04x}'.format(message['transaction_id'])
    if 1 <= function_code <= 4:
        first_address_hex = '{:04x}'.format(message['address'])
        count_hex = '{:04x}'.format(message['count'])
        length_hex = '0006'
        print(transaction_id_hex
              + protocol_code
              + length_hex
              + unit_address_hex
              + function_code_hex
              + first_address_hex
              + count_hex)
        return (transaction_id_hex
                + protocol_code
                + length_hex
                + unit_address_hex
                + function_code_hex
                + first_address_hex
                + count_hex)
    elif function_code == 5:
        first_address_hex = '{:04x}'.format(message['address'])
        status_hex = 'FF00' if message['status'] else '0000'
        length_hex = '0006'
        print(transaction_id_hex
              + protocol_code
              + length_hex
              + unit_address_hex
              + function_code_hex
              + first_address_hex
              + status_hex)
        return (transaction_id_hex
                + protocol_code
                + length_hex
                + unit_address_hex
                + function_code_hex
                + first_address_hex
                + status_hex)
    elif function_code == 6:
        first_address_hex = '{:04x}'.format(message['address'])
        data_hex = '{:04x}'.format(message['data'])
        length_hex = '0006'
        print(transaction_id_hex
              + protocol_code
              + length_hex
              + unit_address_hex
              + function_code_hex
              + first_address_hex
              + data_hex)
        return (transaction_id_hex
                + protocol_code
                + length_hex
                + unit_address_hex
                + function_code_hex
                + first_address_hex
                + data_hex)
    elif function_code == 16:
        first_address_hex = '{:04x}'.format(message['address'])
        length_hex = '{:04x}'.format(1 + 1 + 2 + 2 + 1 + 2 * len(message['data']))
        data_hex = ''.join(['{:04x}'.format(x) for x in message['data']])
        register_count_hex = '{:04x}'.format(len(message['data']))
        byte_count_hex = '{:02x}'.format(2 * len(message['data']))
        print(transaction_id_hex
              + protocol_code
              + length_hex
              + unit_address_hex
              + function_code_hex
              + first_address_hex
              + register_count_hex
              + byte_count_hex
              + data_hex)
        return (transaction_id_hex
                + protocol_code
                + length_hex
                + unit_address_hex
                + function_code_hex
                + first_address_hex
                + register_count_hex
                + byte_count_hex
                + data_hex)
    elif function_code == 15:
        first_address_hex = '{:04x}'.format(message['address'])
        length_hex = '{:04x}'.format(1 + 1 + 2 + 2 + 1 + math.ceil(len(message['data']) / 8))
        data_hex = ''.join(['{:02x}'.format(int(''.join(z), 2)) for z in
                            [x[::-1] for x in [message['data'][i:i + 8] for i in range(0, len(message['data']), 8)]]])
        coil_count_hex = '{:04x}'.format(len(message['data']))
        byte_count_hex = '{:02x}'.format(math.ceil(len(message['data'])/8))
        return (transaction_id_hex
                + protocol_code
                + length_hex
                + unit_address_hex
                + function_code_hex
                + first_address_hex
                + coil_count_hex
                + byte_count_hex
                + data_hex)
