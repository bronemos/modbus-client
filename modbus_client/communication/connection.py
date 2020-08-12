import asyncio

import aiohttp

from modbus_client.communication import serializer
from modbus_client.resources.codes import Codes

conf = {
    'host': 'localhost',
    'port': '3456'
}


class Connection:
    _pending_responses = dict()
    transaction_id = 0

    async def connect(self):
        """
        Establishes connection to a websocket tunnel.

        Returns:
            Response to the connection request.
        """
        self.session = aiohttp.ClientSession()
        self.ws = await self.session.ws_connect(
            'ws://' + ':'.join([conf['host'], conf['port']]) + '/ws')
        return (await self.ws.receive()).data

    async def read_writer(self, function_code: int, transaction_id: int, unit_address: int, first_address: int,
                          count: int) -> dict:
        """
        Serializes a message based on parameters and sends it.

        Args:
            function_code (int): Unique function code.
            transaction_id (int): ID of the transaction.
            unit_address (int): Address of the referenced unit.
            first_address (int): Starting address.
            count (int): Number of items to be read.

        Returns:
            response_dict (dict): Dictionary created as a response to the request.
        """
        pending_response = asyncio.Future()
        self._pending_responses[transaction_id] = pending_response
        serialized_message = serializer.serialize_read(function_code, transaction_id, unit_address,
                                                       first_address, count)
        await self.ws.send_bytes(bytes.fromhex(serialized_message))
        response_dict = await pending_response
        response_dict['raw_request'] = bytes.fromhex(serialized_message[16:])
        response_dict['address'] = first_address
        response_dict['count'] = count
        self.transaction_id += 1
        return response_dict

    async def read_coils(self, unit_address: int, first_address: int, count: int) -> dict:
        """
        Reads coil statuses on the device.

        Args:
            unit_address (int): Address of the referenced unit.
            first_address (int): Starting address.
            count (int): Number of coils to be read.

        Returns:
            response_dict (dict): Dictionary created as a response to the request.
        """
        return await self.read_writer(Codes.READ_COILS.value, self.transaction_id, unit_address, first_address, count)

    async def read_discrete_inputs(self, unit_address: int, first_address: int, count: int) -> dict:
        """
        Reads discrete inputs on the device.

        Args:
            unit_address (int): Address of the referenced unit.
            first_address (int): Starting address.
            count (int): Number of discrete inputs to be read.

        Returns:
            response_dict (dict): Dictionary created as a response to the request.
        """
        return await self.read_writer(Codes.READ_DISCRETE_INPUTS.value, self.transaction_id, unit_address,
                                      first_address,
                                      count)

    async def read_holding_registers(self, unit_address: int, first_address: int, count: int) -> dict:
        """
        Reads holding registers on the device.

        Args:
            unit_address (int): Address of the referenced unit.
            first_address (int): Starting address.
            count (int): Number of holding registers to be read.

        Returns:
            response_dict (dict): Dictionary created as a response to the request.
        """
        return await self.read_writer(Codes.READ_HOLDING_REGISTERS.value, self.transaction_id, unit_address,
                                      first_address,
                                      count)

    async def read_input_registers(self, unit_address: int, first_address: int, count: int) -> dict:
        """
        Reads input registers on the device.

        Args:
            unit_address (int): Address of the referenced unit.
            first_address (int): Starting address.
            count (int): Number of input registers to be read.

        Returns:
            response_dict (dict): Dictionary created as a response to the request.
        """
        return await self.read_writer(Codes.READ_INPUT_REGISTERS.value, self.transaction_id, unit_address,
                                      first_address,
                                      count)

    async def write_single_coil(self, unit_address: int, address: int, status: bool) -> dict:
        """
        Writes to a single coil on the device.

        Args:
            unit_address (int): Address of the referenced unit.
            address (int): Address to be written to.
            status (bool): Status of the coil (True if set False otherwise)

        Returns:
            response_dict (dict): Dictionary created as a response to the request.
        """
        pending_response = asyncio.Future()
        self._pending_responses[self.transaction_id] = pending_response
        serialized_message = serializer.serialize_write_single_coil(self.transaction_id, unit_address, address,
                                                                    status)
        await self.ws.send_bytes(bytes.fromhex(serialized_message))
        response_dict = await pending_response
        response_dict['raw_request'] = bytes.fromhex(serialized_message[16:])
        response_dict['address'] = address
        self.transaction_id += 1
        return response_dict

    async def write_single_register(self, unit_address: int, address: int, data: int) -> dict:
        """
        Writes to a single register on the device.

        Args:
            unit_address (int): Address of the referenced unit.
            address (int): Address to be written to.
            data (int): Data to be written in the register.

        Returns:
            response_dict (dict): Dictionary created as a response to the request.
        """
        pending_response = asyncio.Future()
        self._pending_responses[self.transaction_id] = pending_response
        serialized_message = serializer.serialize_write_single_register(self.transaction_id, unit_address, address,
                                                                        data)
        await self.ws.send_bytes(bytes.fromhex(serialized_message))
        response_dict = await pending_response
        response_dict['raw_request'] = bytes.fromhex(serialized_message[16:])
        response_dict['address'] = address
        self.transaction_id += 1
        return response_dict

    async def write_multiple_registers(self, unit_address: int, first_address: int, data: list) -> dict:
        """
        Writes to multiple registers.

        Args:
            unit_address (int): Address of the referenced unit.
            first_address (int): Starting address.
            data (list): List of data to be written.

        Returns:
            response_dict (dict): Dictionary created as a response to the request.
        """
        pending_response = asyncio.Future()
        self._pending_responses[self.transaction_id] = pending_response
        serialized_message = serializer.serialize_write_multiple_registers(self.transaction_id, unit_address,
                                                                           first_address,
                                                                           data)
        await self.ws.send_bytes(bytes.fromhex(serialized_message))
        response_dict = await pending_response
        response_dict['raw_request'] = bytes.fromhex(serialized_message[16:])
        response_dict['address'] = first_address
        self.transaction_id += 1
        return response_dict

    async def write_multiple_coils(self, unit_address: int, first_address: int, data: list) -> dict:
        """
        Writes to multiple coils.

        Args:
            unit_address (int): Address of the referenced unit.
            first_address (int): Starting address.
            data (list): List of data to be written.

        Returns:
            response_dict (dict): Dictionary created as a response to the request.
        """
        pending_response = asyncio.Future()
        self._pending_responses[self.transaction_id] = pending_response
        serialized_message = serializer.serialize_write_multiple_coils(self.transaction_id, unit_address, first_address,
                                                                       data)
        await self.ws.send_bytes(bytes.fromhex(serialized_message))
        response_dict = await pending_response
        response_dict['raw_request'] = bytes.fromhex(serialized_message[16:])
        response_dict['address'] = first_address
        self.transaction_id += 1
        return response_dict

    async def ws_reader(self):
        """
        Awaits a message, deserializes it and puts it as a result of a corresponding pending future.
        """
        while True:
            message = serializer.deserialize_message((await self.ws.receive()).data)
            if type(message) != str:
                self._pending_responses[message['transaction_id']].set_result(message)
