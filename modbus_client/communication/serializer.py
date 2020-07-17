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
unit_address = '01'


async def serialize():
    executor = ThreadPoolExecutor(max_workers=1)
    ws = await aiohttp.ClientSession().ws_connect(
        'ws://' + ':'.join([conf['host'], conf['port']]) + '/ws')

    async def ws_reader():

        def deserialize_message(message):
            if type(message) == bytes:
                function_code = message[7]
                print(message)
                message_hex = message.hex()
                print(message_hex)
                if function_code == 1:
                    coils_set = list()
                    coil_status = ''.join(
                        ['{:04b}'.format(int((x + y)[::-1]), 16) for x, y in zip(message_hex[::2], message_hex[1::2])])
                    for no, status in enumerate(coil_status):
                        if status == '1':
                            coils_set.append(str(no))
                    print(f'coil status: {coil_status}, {len(coil_status)}')
                    return {'coils_set': coils_set}
                elif function_code == 2:
                    pass
                elif function_code == 3:
                    pass
                elif function_code == 4:
                    pass
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
        function_code = message['function_code']
        print(function_code)
        function_code_hex = '{:02x}'.format(function_code)
        message_id_hex = '{:04x}'.format(message['message_id'])
        if 1 <= function_code <= 4:
            first_address_hex = '{:04x}'.format(message['address'])
            count_hex = '{:04x}'.format(message['count'])
            print((message_id_hex
                   + protocol_code
                   + '0006'
                   + unit_address
                   + function_code_hex
                   + first_address_hex
                   + count_hex))
            return (message_id_hex
                    + protocol_code
                    + '0006'
                    + unit_address
                    + function_code_hex
                    + first_address_hex
                    + count_hex)
        elif function_code == 5:
            first_address_hex = '{:04x}'.format(message['first_address'])
            status_hex = '0000' if message['status'] else 'FF00'
            return (message_id_hex
                    + protocol_code
                    + '0006'
                    + unit_address
                    + function_code_hex
                    + first_address_hex
                    + status_hex)

    try:
        return serialize_message(req_queue.get())
    except queue.Empty:
        return


def start():
    asyncio.new_event_loop().run_until_complete(serialize())
