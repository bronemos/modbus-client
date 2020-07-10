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


async def serialize():
    executor = ThreadPoolExecutor(max_workers=1)
    ws = await aiohttp.ClientSession().ws_connect(
        'ws://' + ':'.join([conf['host'], conf['port']]) + '/ws')

    async def ws_reader():
        while True:
            msg = await ws.receive()
            print(msg)
            res_queue.put(msg.data)

    async def ws_writer():
        while True:
            user_message = await asyncio.get_event_loop().run_in_executor(executor, ext_get_user_message)
            try:
                await ws.send_bytes(bytes.fromhex(user_message))
            except Exception as e:
                print(e)

    ws_reader_future = asyncio.ensure_future(ws_reader())
    ws_writer_future = asyncio.ensure_future(ws_writer())
    await asyncio.wait([ws_reader_future, ws_writer_future], return_when=asyncio.FIRST_COMPLETED)
    ws_reader_future.cancel()
    ws_writer_future.cancel()
    await ws.close()


def ext_get_user_message():
    try:
        x = req_queue.get()
        return x
    except queue.Empty:
        return


def start():
    asyncio.new_event_loop().run_until_complete(serialize())
