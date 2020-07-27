import asyncio

import aiohttp

from modbus_client.communication import serializer

conf = {
    'host': 'localhost',
    'port': '3456'
}


class Connection:
    _pending_responses = dict()

    async def connect(self):
        self.session = aiohttp.ClientSession()
        self.ws = await self.session.ws_connect(
            'ws://' + ':'.join([conf['host'], conf['port']]) + '/ws')
        return (await self.ws.receive()).data

    async def ws_writer(self, message: dict):
        transaction_id = message['message_id']
        pending_response = asyncio.Future()
        self._pending_responses[transaction_id] = pending_response
        await self.ws.send_bytes(bytes.fromhex(serializer.serialize_message(message)))
        return await pending_response

    async def ws_reader(self):
        while True:
            message = serializer.deserialize_message((await self.ws.receive()).data)
            if type(message) != str:
                self._pending_responses[message['message_id']].set_result(message)
