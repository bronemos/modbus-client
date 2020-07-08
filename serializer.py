import asyncio
import aiohttp
import json
from threading import Thread


class Serializer:
    conf = {
        'host': 'localhost',
        'port': '3456'
    }
    to_send = False

    async def serialize(self):
        ws = await aiohttp.ClientSession().ws_connect(
            'ws://' + ':'.join([self.conf['host'], self.conf['port']]) + '/ws')

        async def ws_reader():
            while True:
                msg = await ws.receive()
                print(msg)

        async def ws_writer():
            while True:
                if self.to_send:
                    try:
                        await ws.send_bytes(bytes.fromhex('00 05 00 00 00 06 01 01 00 00 00 01'))
                    except Exception as e:
                        print(e)
                    self.to_send = False

        ws_reader_future = asyncio.ensure_future(ws_reader())
        ws_writer_future = asyncio.ensure_future(ws_writer())
        await asyncio.wait([ws_reader_future, ws_writer_future], return_when=asyncio.FIRST_COMPLETED)
        ws_reader_future.cancel()
        ws_writer_future.cancel()
        await ws.close()

    def start_loop(self):
        asyncio.new_event_loop().run_until_complete(self.serialize())

    def __init__(self):
        loop_thread = Thread(target=self.start_loop)
        loop_thread.start()
