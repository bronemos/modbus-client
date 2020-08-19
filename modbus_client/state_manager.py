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

    def __init__(self, refresh_time=3):
        super(StateManager, self).__init__()
        self._refresh_time = refresh_time
        self.user_req_queue = Queue()
        self.backend = Backend()
        self._executor = ThreadPoolExecutor(max_workers=1)
        self.current_state = dict()
        self._connection = Connection()

    def run_loop(self):
        """
        Initiates the loop thread of the state manager.
        """
        self._disconnecting = False
        loop_thread = Thread(
            target=lambda: asyncio.new_event_loop().run_until_complete(self._state_manager_loop()), daemon=True)
        loop_thread.start()

    async def _state_manager_loop(self):
        writer_future = asyncio.ensure_future(self._write_loop())
        await asyncio.wait([writer_future, ], return_when=asyncio.FIRST_COMPLETED)
        writer_future.cancel()

    async def _write_loop(self):
        while True:
            message = await asyncio.get_event_loop().run_in_executor(self._executor, self._ext_get_message)
            if type(message) == str:
                if message == 'CONN':
                    print('here')
                    try:
                        connection_response = await self._connection.connect()
                        self.update.emit(connection_response)
                        if connection_response == 'ACK':
                            self.counter_future = asyncio.ensure_future(self._counter())
                    except Exception:
                        self.update.emit('wstunnel_error')
                elif message == 'DC':
                    self._disconnecting = True
                    self.update_counter.emit(0)
                    await self._connection.session.close()
                    self._connection.ws_reader_future.cancel()
                    self.counter_future.cancel()
                    self._disconnecting = False

                elif message == 'update_historian':
                    self.update_historian.emit({'request_history': await self.backend.get_request_history(),
                                                'response_history': await self.backend.get_response_history()})

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
                if not self._disconnecting:
                    self.update_counter.emit(i)

    def _ext_get_message(self):
        return self.user_req_queue.get()
