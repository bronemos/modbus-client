import asyncio
import queue
from concurrent.futures import ThreadPoolExecutor

import aiohttp

conf = {
    'host': 'localhost',
    'port': '3456'
}

req_queue = queue.Queue()
res_queue = queue.Queue()

protocol_code = '0000'

response_first_address = 0


async def serialize():
    executor = ThreadPoolExecutor(max_workers=1)
    ws = await aiohttp.ClientSession().ws_connect(
        'ws://' + ':'.join([conf['host'], conf['port']]) + '/ws')

    async def ws_reader():

        def deserialize_message(message):
            if type(message) == bytes:
                function_code = message[7]
                print(f"function code:{function_code}")
                message_hex = message[9:].hex()
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
                    return {'set_list': set_list}
                elif function_code == 3 or function_code == 4:
                    data_list = list()
                    data_list.extend(
                        [str(int(''.join(message_hex[i:i + 4]), 16)) for i in range(0, len(message_hex), 4)])
                    print(data_list)
                    return {'register_data': data_list}
                elif function_code:
                    pass

            else:
                print(message)
            return message

        while True:
            message = await ws.receive()
            res_queue.put(deserialize_message(message.data))

    async def ws_writer():
        while True:
            user_message = await asyncio.get_event_loop().run_in_executor(executor, ext_get_user_message)
            if user_message == 'DC':
                return
            try:
                await ws.send_bytes(bytes.fromhex(user_message))
            except Exception as e:
                print(e)

    ws_reader_future = asyncio.ensure_future(ws_reader())
    ws_writer_future = asyncio.ensure_future(ws_writer())
    await asyncio.wait([ws_reader_future, ws_writer_future], return_when=asyncio.FIRST_COMPLETED)
    ws_reader_future.cancel()
    ws_writer_future.cancel()


def ext_get_user_message():
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

    try:
        return serialize_message(req_queue.get())
    except queue.Empty:
        return


def start():
    asyncio.new_event_loop().run_until_complete(serialize())
