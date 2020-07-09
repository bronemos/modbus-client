import asyncio
import aiohttp
import json
from threading import Thread

conf = {
    'host': 'localhost',
    'port': '3456'
}
to_send = False

async def serialize():
    ws = await aiohttp.ClientSession().ws_connect(
        'ws://' + ':'.join([conf['host'], conf['port']]) + '/ws')


    async def ws_reader():
        while True:
            msg = await ws.receive()
            print(msg)

    async def ws_writer():
        global to_send
        while True:
            await asyncio.sleep(1)
            if to_send:
                try:
                    await ws.send_bytes(bytes.fromhex('00 05 00 00 00 06 01 01 00 00 00 01'))
                    to_send = False
                except Exception as e:
                    print(e)

    ws_reader_future = asyncio.ensure_future(ws_reader())
    ws_writer_future = asyncio.ensure_future(ws_writer())
    await asyncio.wait([ws_reader_future, ws_writer_future])
    ws_reader_future.cancel()
    ws_writer_future.cancel()
    await ws.close()


def start():
    asyncio.new_event_loop().run_until_complete(serialize())
