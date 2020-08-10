import asyncio
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Thread

from PySide2.QtCore import QObject, Signal

from modbus_client.communication.connection import Connection
from modbus_client.db.backend import Backend
from modbus_client.resources.codes import Codes


class StateManager(QObject):
    executor = ThreadPoolExecutor(max_workers=1)
    update = Signal(dict)
    current_state = dict()
    update_counter = Signal(int)
    initiate_live_view_update = Signal()
    update_view = Signal(dict)

    def __init__(self, refresh_time=3):
        super(StateManager, self).__init__()
        self.refresh_time = refresh_time
        self.user_req_queue = Queue()
        self.backend = Backend()

    def run_loop(self):
        self.disconnecting = False
        self.loop_thread = Thread(
            target=lambda: asyncio.new_event_loop().run_until_complete(self._state_manager_loop()), daemon=True)
        self.loop_thread.start()

    async def _state_manager_loop(self):
        self.connection = Connection()
        try:
            connection_response = await self.connection.connect()
            self.update.emit(connection_response)
        except Exception:
            self.update.emit('wstunnel_error')

        writer_future = asyncio.ensure_future(self.write_loop())
        reader_future = asyncio.ensure_future(self.connection.ws_reader())
        counter_future = asyncio.ensure_future(self.counter())
        await asyncio.wait([writer_future, reader_future, counter_future], return_when=asyncio.FIRST_COMPLETED)
        counter_future.cancel()
        writer_future.cancel()
        reader_future.cancel()

    async def write_loop(self):
        while True:
            message = await asyncio.get_event_loop().run_in_executor(self.executor, self._ext_get_message)
            if message == 'DC':
                self.disconnecting = True
                self.update_counter.emit(0)
                await self.connection.session.close()
                return

            if message['function_code'] == Codes.READ_COILS.value:
                response = await self.connection.read_coils(message['unit_address'],
                                                            message['address'], message['count'])

            elif message['function_code'] == Codes.READ_DISCRETE_INPUTS.value:
                response = await self.connection.read_discrete_inputs(message['unit_address'],
                                                                      message['address'], message['count'])

            elif message['function_code'] == Codes.READ_HOLDING_REGISTERS.value:
                response = await self.connection.read_holding_registers(message['unit_address'],
                                                                        message['address'], message['count'])

            elif message['function_code'] == Codes.READ_INPUT_REGISTERS.value:
                response = await self.connection.read_input_registers(message['unit_address'],
                                                                      message['address'], message['count'])

            elif message['function_code'] == Codes.WRITE_SINGLE_COIL.value:
                response = await self.connection.write_single_coil(message['unit_address'],
                                                                   message['address'], message['status'])

            elif message['function_code'] == Codes.WRITE_SINGLE_REGISTER.value:
                response = await self.connection.write_single_register(message['unit_address'],
                                                                       message['address'], message['data'])

            elif message['function_code'] == Codes.WRITE_MULTIPLE_COILS.value:
                response = await self.connection.write_multiple_coils(message['unit_address'],
                                                                      message['address'], message['data'])

            elif message['function_code'] == Codes.WRITE_MULTIPLE_REGISTERS.value:
                response = await self.connection.write_multiple_registers(message['unit_address'],
                                                                          message['address'], message['data'])

            if message['user_generated']:
                try:
                    self.backend.insert_request_history(response)
                    self.backend.insert_response_history(response)
                except Exception as e:
                    print(e)
                self.update.emit(response)
            else:
                self.update_view.emit(response)

    async def counter(self):
        while True:
            self.initiate_live_view_update.emit()
            for i in range(1, 101):
                await asyncio.sleep(self.refresh_time / 100)
                if not self.disconnecting:
                    self.update_counter.emit(i)

    def _ext_get_message(self):
        return self.user_req_queue.get()
