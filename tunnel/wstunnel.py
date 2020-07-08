import asyncio
import aiohttp.web
import contextlib
import json
import sys
from datetime import datetime


class WSTunnel:
    conf = {
        'ws': {
            'host': '0.0.0.0',
            'port': 3456},
        'modbus': {
            'host': 'localhost',
            'port': 502}}

    async def ws_handler(self, request):
        ws = aiohttp.web.WebSocketResponse()
        await ws.prepare(request)
        try:
            print(datetime.now().strftime("%H:%M:%S") + " Connection established")
            # conn_msg_str = await ws.receive_str()
            # conn_msg = json.loads(conn_msg_str)
            reader, writer = await asyncio.open_connection(
                self.conf['modbus']['host'], self.conf['modbus']['port'])
        except Exception:
            return ws
        await ws.send_str('ACK')

        async def tcp_read_loop():
            while True:
                try:
                    msg = await reader.read(1024)
                except Exception:
                    break
                if not msg:
                    break
                await ws.send_bytes(msg)

        async def ws_read_loop():
            while True:
                try:
                    msg = await ws.receive_bytes()
                    #print(datetime.now().strftime("%H:%M:%S") + msg)
                except Exception:
                    break
                writer.write(msg)

        tcp_future = asyncio.ensure_future(tcp_read_loop())
        ws_future = asyncio.ensure_future(ws_read_loop())
        await asyncio.wait(
            [tcp_future, ws_future], return_when=asyncio.FIRST_COMPLETED)
        tcp_future.cancel()
        ws_future.cancel()

        with contextlib.suppress(Exception):
            writer.write_eof()
        with contextlib.suppress(Exception):
            writer.close()

        return ws

    def __init__(self):
        app = aiohttp.web.Application()
        app.router.add_route('*', '/ws', self.ws_handler)
        aiohttp.web.run_app(app,
                            host=self.conf['ws']['host'], port=self.conf['ws']['port'],
                            shutdown_timeout=0)


if __name__ == "__main__":
    WSTunnel()
