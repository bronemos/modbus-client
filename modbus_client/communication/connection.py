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
        transaction_id = message['transaction_id']
        pending_response = asyncio.Future()
        self._pending_responses[transaction_id] = pending_response
        serialized_message = serializer.serialize_message(message)
        await self.ws.send_bytes(bytes.fromhex(serialized_message))
        response_dict = await pending_response
        response_dict['raw_request'] = bytes.fromhex(serialized_message[16:])
        response_dict['address'] = message['address']
        response_dict['count'] = message['count']
        return response_dict

    async def ws_reader(self):
        while True:
            message = serializer.deserialize_message((await self.ws.receive()).data)
            if type(message) != str:
                self._pending_responses[message['transaction_id']].set_result(message)
