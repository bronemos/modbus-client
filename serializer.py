import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from time import sleep
import json
from threading import Thread

conf = {
    'host': 'localhost',
    'port': '3456'
}
to_send = False


async def serialize():
    executor = ThreadPoolExecutor(max_workers=1)
    ws = await aiohttp.ClientSession().ws_connect(
        'ws://' + ':'.join([conf['host'], conf['port']]) + '/ws')

    async def ws_reader():
        while True:
            msg = await ws.receive()
            print(msg)

    async def ws_writer():
        global to_send
        while True:
            user_action = await asyncio.get_event_loop().run_in_executor(executor, ext_get_user_action)
            print(user_action)
            if to_send:
                try:
                    await ws.send_bytes(bytes.fromhex('00 05 00 00 00 06 01 01 00 00 00 01'))
                    to_send = False
                except Exception as e:
                    print(e)

    ws_reader_future = asyncio.ensure_future(ws_reader())
    ws_writer_future = asyncio.ensure_future(ws_writer())
    await asyncio.wait([ws_reader_future, ws_writer_future], return_when=asyncio.FIRST_COMPLETED)
    ws_reader_future.cancel()
    ws_writer_future.cancel()
    await ws.close()


def ext_get_user_action():
    sleep(1)
    return 5


def start():
    asyncio.new_event_loop().run_until_complete(serialize())
