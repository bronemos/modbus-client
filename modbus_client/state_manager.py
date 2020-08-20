import asyncio
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Thread

from PySide2.QtCore import QObject, Signal

from modbus_client.communication.connection import Connection
from modbus_client.db.backend import Backend
from modbus_client.resources.codes import Codes


class StateManager(QObject):
    """
    Used for communication between GUI and Connection module while monitoring and storing current state of the device
    that it's connected to.
    """
    update = Signal(dict)
    update_counter = Signal(int)
    initiate_live_view_update = Signal()
    update_view = Signal(dict)
    update_historian = Signal(dict)
    export_response = Signal(list)
    export_request = Signal(list)

    def __init__(self, refresh_time=3):
        super(StateManager, self).__init__()
        self._refresh_time = refresh_time
        self.user_req_queue = Queue()
        self.backend = Backend()
        self._executor = ThreadPoolExecutor(max_workers=1)
        self.current_state = dict()
        self._connection = Connection()
        self._connected = False

    def run_loop(self):
        """
        Initiates the loop thread of the state manager.
        """
        loop_thread = Thread(
            target=lambda: asyncio.new_event_loop().run_until_complete(self._write_loop()), daemon=True)
        loop_thread.start()

    async def _write_loop(self):
        while True:
            message = await asyncio.get_event_loop().run_in_executor(self._executor, self._ext_get_message)
            if type(message) == str:
                if message == 'CONN':
                    try:
                        connection_response = await self._connection.connect()
                        self.update.emit(connection_response)
                        if connection_response == 'ACK':
                            self.counter_future = asyncio.ensure_future(self._counter())
                            self._connected = True
                    except Exception:
                        self.update.emit('wstunnel_error')
                elif message == 'DC':
                    if self._connected:
                        await self._connection.close()
                        #todo future not cancelling
                        self.counter_future.cancel()
                        await self.counter_future
                    self.update_counter.emit(0)
                    self._connected = False

                elif message == 'update_historian':
                    self.update_historian.emit({'request_history': await self.backend.get_request_history(),
                                                'response_history': await self.backend.get_response_history()})

                elif message == 'export_request':
                    self.export_response.emit(await self.backend.get_request_history())

                elif message == 'export_response':
                    self.export_request.emit(await self.backend.get_response_history())

            else:

                if message['function_code'] == Codes.READ_COILS.value:
                    response = await self._connection.read_coils(message['unit_address'],
                                                                 message['address'], message['count'])

                elif message['function_code'] == Codes.READ_DISCRETE_INPUTS.value:
                    response = await self._connection.read_discrete_inputs(message['unit_address'],
                                                                           message['address'], message['count'])

                elif message['function_code'] == Codes.READ_HOLDING_REGISTERS.value:
                    response = await self._connection.read_holding_registers(message['unit_address'],
                                                                             message['address'], message['count'])

                elif message['function_code'] == Codes.READ_INPUT_REGISTERS.value:
                    response = await self._connection.read_input_registers(message['unit_address'],
                                                                           message['address'], message['count'])

                elif message['function_code'] == Codes.WRITE_SINGLE_COIL.value:
                    response = await self._connection.write_single_coil(message['unit_address'],
                                                                        message['address'], message['status'])

                elif message['function_code'] == Codes.WRITE_SINGLE_REGISTER.value:
                    response = await self._connection.write_single_register(message['unit_address'],
                                                                            message['address'], message['data'])

                elif message['function_code'] == Codes.WRITE_MULTIPLE_COILS.value:
                    response = await self._connection.write_multiple_coils(message['unit_address'],
                                                                           message['address'], message['data'])

                elif message['function_code'] == Codes.WRITE_MULTIPLE_REGISTERS.value:
                    response = await self._connection.write_multiple_registers(message['unit_address'],
                                                                               message['address'], message['data'])

                if message['user_generated']:
                    try:
                        await self.backend.insert_request_history(response['transaction_id'], response['unit_address'],
                                                                  response['function_code'], response['raw_request'])
                        await self.backend.insert_response_history(response['transaction_id'], response['unit_address'],
                                                                   response['function_code'], response['raw_data'])
                        self.update_historian.emit({'request_history': await self.backend.get_request_history(),
                                                    'response_history': await self.backend.get_response_history()})
                    except Exception as e:
                        print(e)
                    self.update.emit(response)
                else:
                    self.update_view.emit(response)

    async def _counter(self):
        while True:
            self.initiate_live_view_update.emit()
            for i in range(1, 101):
                await asyncio.sleep(self._refresh_time / 100)
                self.update_counter.emit(i)

    def _ext_get_message(self):
        return self.user_req_queue.get()
