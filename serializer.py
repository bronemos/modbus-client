import asyncio
import aiohttp
import queue

from concurrent.futures import ThreadPoolExecutor

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
                print(message.hex())

            else:
                print(message)
            return message
        while True:
            message = await ws.receive()
            res_queue.put(deserialize_message(message.data))

    async def ws_writer():
        while True:
            user_message = await asyncio.get_event_loop().run_in_executor(executor, ext_get_user_message)
            if user_message == "DC":
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
        function_code_hex = '{:02x}'.format(function_code)
        message_id_hex = '{:04x}'.format(message['message_id'])
        if 1 <= function_code <= 4:
            first_address_hex = '{:04x}'.format(message['first_address'])
            count_hex = '{:04x}'.format(message['count'])
            return message_id_hex + protocol_code + '0006' + unit_address + function_code_hex + first_address_hex + count_hex
        elif function_code == 5:
            first_address_hex = '{:04x}'.format(message['first_address'])
            status_hex = '0000' if message['status'] else 'FF00'
            return message_id_hex + protocol_code + '0006' + unit_address + function_code_hex + first_address_hex + status_hex

    try:
        return serialize_message(req_queue.get())
    except queue.Empty:
        return


def start():
    asyncio.new_event_loop().run_until_complete(serialize())
