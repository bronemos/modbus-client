protocol_code = '0000'

response_first_address = 0


def deserialize_message(message):
    if type(message) == bytes:
        message_id = int(message[0:2].hex(), 16)
        unit_address = message[6]
        function_code = message[7]
        print(f"function code:{function_code}")
        message_hex = message[9:].hex()
        raw_data = message[8:]
        print("msg hex: ", message_hex)
        if function_code == 1 or function_code == 2:
            set_list = list()
            statuses = ''.join([z[::-1] for z in
                                ['{:08b}'.format(int((x + y), 16)) for x, y in
                                 zip(message_hex[::2], message_hex[1::2])]])
            print(statuses)
            for no, status in enumerate(statuses):
                if status == '1':
                    set_list.append(str(no + response_first_address))
            print(f'coil status: {statuses}, {len(statuses)}')
            return {'message_id': message_id,
                    'unit_address': unit_address,
                    'function_code': function_code,
                    'set_list': set_list,
                    'raw_data': raw_data}
        elif function_code == 3 or function_code == 4:
            data_list = list()
            data_list.extend(
                [str(int(''.join(message_hex[i:i + 4]), 16)) for i in range(0, len(message_hex), 4)])
            print(data_list)
            return {'message_id': message_id,
                    'unit_address': unit_address,
                    'function_code': function_code,
                    'register_data': data_list,
                    'raw_data': raw_data}
        elif function_code:
            pass

    else:
        print(message)
    return message


def serialize_message(message):
    global response_first_address
    function_code = message['function_code']
    response_first_address = message['address']
    unit_address_hex = '{:02x}'.format(message['unit_address'])
    function_code_hex = '{:02x}'.format(function_code)
    message_id_hex = '{:04x}'.format(message['message_id'])
    if 1 <= function_code <= 4:
        first_address_hex = '{:04x}'.format(message['address'])
        count_hex = '{:04x}'.format(message['count'])
        length_hex = '0006'
        print(message_id_hex
              + protocol_code
              + length_hex
              + unit_address_hex
              + function_code_hex
              + first_address_hex
              + count_hex)
        return (message_id_hex
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
        print(message_id_hex
              + protocol_code
              + length_hex
              + unit_address_hex
              + function_code_hex
              + first_address_hex
              + status_hex)
        return (message_id_hex
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
        print(message_id_hex
              + protocol_code
              + length_hex
              + unit_address_hex
              + function_code_hex
              + first_address_hex
              + data_hex)
        return (message_id_hex
                + protocol_code
                + length_hex
                + unit_address_hex
                + function_code_hex
                + first_address_hex
                + data_hex)
    elif function_code == 16:
        first_address_hex = '{:04x}'.format(message['address'])
        length_hex = '{:04x}'.format((1 + 1 + 2 + 2 + 1 + 2 * len(message['data'])))
        data_hex = ''.join(['{:04x}'.format(x) for x in message['data']])
        register_count_hex = '{:04x}'.format(len(message['data']))
        byte_count_hex = '{:02x}'.format(2 * len(message['data']))
        print(message_id_hex
              + protocol_code
              + length_hex
              + unit_address_hex
              + function_code_hex
              + first_address_hex
              + register_count_hex
              + byte_count_hex
              + data_hex)
        return (message_id_hex
                + protocol_code
                + length_hex
                + unit_address_hex
                + function_code_hex
                + first_address_hex
                + register_count_hex
                + byte_count_hex
                + data_hex)
