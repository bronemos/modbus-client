import asyncio
from contextlib import suppress

import aiohttp

from modbus_client.communication import serializer
from modbus_client.resources.codes import Codes

conf = {
    'host': 'localhost',
    'port': '3456'
}


class Connection:

    async def connect(self):
        """
        Establishes connection to a websocket tunnel.

        Returns:
            Response to the connection request.
        """
        self._pending_responses = dict()
        self._transaction_id = 0
        self.session = aiohttp.ClientSession()
        self._ws = await self.session.ws_connect(
            'ws://' + ':'.join([conf['host'], conf['port']]) + '/ws')
        response = (await self._ws.receive()).data
        self.ws_reader_future = asyncio.ensure_future(self.ws_reader())
        return response

    async def _read_writer(self, function_code: int, transaction_id: int, unit_address: int, first_address: int,
                           count: int) -> dict:

        pending_response = asyncio.Future()
        self._pending_responses[transaction_id] = pending_response
        serialized_message = serializer.serialize_read(function_code, transaction_id, unit_address, first_address,
                                                       count)
        await self._ws.send_bytes(bytes.fromhex(serialized_message))
        response_dict = await pending_response
        response_dict['raw_request'] = bytes.fromhex(serialized_message[16:])
        response_dict['address'] = first_address
        response_dict['count'] = count
        self._transaction_id += 1
        return response_dict

    async def read_coils(self, unit_address: int, first_address: int, count: int) -> dict:
        """
        Reads coil statuses on the device.

        Args:
            unit_address: Address of the referenced unit.
            first_address: Starting address.
            count: Number of coils to be read.

        Returns:
            dict: Dictionary created as a response to the request.
        """
        return await self._read_writer(Codes.READ_COILS.value, self._transaction_id, unit_address, first_address, count)

    async def read_discrete_inputs(self, unit_address: int, first_address: int, count: int) -> dict:
        """
        Reads discrete inputs on the device.

        Args:
            unit_address: Address of the referenced unit.
            first_address: Starting address.
            count: Number of discrete inputs to be read.

        Returns:
            dict: Dictionary created as a response to the request.
        """
        return await self._read_writer(Codes.READ_DISCRETE_INPUTS.value, self._transaction_id, unit_address,
                                       first_address, count)

    async def read_holding_registers(self, unit_address: int, first_address: int, count: int) -> dict:
        """
        Reads holding registers on the device.

        Args:
            unit_address: Address of the referenced unit.
            first_address: Starting address.
            count: Number of holding registers to be read.

        Returns:
            dict: Dictionary created as a response to the request.
        """
        return await self._read_writer(Codes.READ_HOLDING_REGISTERS.value, self._transaction_id, unit_address,
                                       first_address, count)

    async def read_input_registers(self, unit_address: int, first_address: int, count: int) -> dict:
        """
        Reads input registers on the device.

        Args:
            unit_address: Address of the referenced unit.
            first_address: Starting address.
            count: Number of input registers to be read.

        Returns:
            dict: Dictionary created as a response to the request.
        """
        return await self._read_writer(Codes.READ_INPUT_REGISTERS.value, self._transaction_id, unit_address,
                                       first_address, count)

    async def write_single_coil(self, unit_address: int, address: int, status: bool) -> dict:
        """
        Writes to a single coil on the device.

        Args:
            unit_address: Address of the referenced unit.
            address: Address to be written to.
            status: Status of the coil (True if set False otherwise)

        Returns:
            dict: Dictionary created as a response to the request.
        """
        pending_response = asyncio.Future()
        self._pending_responses[self._transaction_id] = pending_response
        serialized_message = serializer.serialize_write_single_coil(self._transaction_id, unit_address, address, status)
        await self._ws.send_bytes(bytes.fromhex(serialized_message))
        response_dict = await pending_response
        response_dict['raw_request'] = bytes.fromhex(serialized_message[16:])
        response_dict['address'] = address
        self._transaction_id += 1
        return response_dict

    async def write_single_register(self, unit_address: int, address: int, data: int) -> dict:
        """
        Writes to a single register on the device.

        Args:
            unit_address: Address of the referenced unit.
            address: Address to be written to.
            data: Data to be written in the register.

        Returns:
            dict: Dictionary created as a response to the request.
        """
        pending_response = asyncio.Future()
        self._pending_responses[self._transaction_id] = pending_response
        serialized_message = serializer.serialize_write_single_register(self._transaction_id, unit_address, address,
                                                                        data)
        await self._ws.send_bytes(bytes.fromhex(serialized_message))
        response_dict = await pending_response
        response_dict['raw_request'] = bytes.fromhex(serialized_message[16:])
        response_dict['address'] = address
        self._transaction_id += 1
        return response_dict

    async def write_multiple_registers(self, unit_address: int, first_address: int, data: list) -> dict:
        """
        Writes to multiple registers.

        Args:
            unit_address: Address of the referenced unit.
            first_address: Starting address.
            data: List of data to be written.

        Returns:
            dict: Dictionary created as a response to the request.
        """
        pending_response = asyncio.Future()
        self._pending_responses[self._transaction_id] = pending_response
        serialized_message = serializer.serialize_write_multiple_registers(self._transaction_id, unit_address,
                                                                           first_address, data)
        await self._ws.send_bytes(bytes.fromhex(serialized_message))
        response_dict = await pending_response
        response_dict['raw_request'] = bytes.fromhex(serialized_message[16:])
        response_dict['address'] = first_address
        self._transaction_id += 1
        return response_dict

    async def write_multiple_coils(self, unit_address: int, first_address: int, data: list) -> dict:
        """
        Writes to multiple coils.

        Args:
            unit_address: Address of the referenced unit.
            first_address: Starting address.
            data: List of data to be written.

        Returns:
            dict: Dictionary created as a response to the request.
        """
        pending_response = asyncio.Future()
        self._pending_responses[self._transaction_id] = pending_response
        serialized_message = serializer.serialize_write_multiple_coils(self._transaction_id, unit_address,
                                                                       first_address, data)
        await self._ws.send_bytes(bytes.fromhex(serialized_message))
        response_dict = await pending_response
        response_dict['raw_request'] = bytes.fromhex(serialized_message[16:])
        response_dict['address'] = first_address
        self._transaction_id += 1
        return response_dict

    async def ws_reader(self):
        """
        Awaits a message, deserializes it and puts it as a result of a corresponding pending future.
        """
        with suppress(asyncio.CancelledError):
            while True:
                message = serializer.deserialize_message((await self._ws.receive()).data)
                if type(message) != str:
                    self._pending_responses[message['transaction_id']].set_result(message)

    async def close(self):
        """
        Closes the connection and cancels the future.
        """
        self.ws_reader_future.cancel()
        await self.ws_reader_future
        await self.session.close()
