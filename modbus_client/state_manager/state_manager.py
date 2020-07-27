import asyncio
import queue
from queue import Queue
from threading import Thread

from PySide2.QtCore import QObject, Signal

from modbus_client.communication.connection import Connection


class StateManager(QObject):
    update = Signal(dict)
    current_state = dict()

    def __init__(self):
        super(StateManager, self).__init__()
        self.req_queue = Queue()

    def run_loop(self):
        loop_thread = Thread(target=lambda: asyncio.new_event_loop().run_until_complete(self._state_manager_loop()))
        loop_thread.start()

    async def _state_manager_loop(self):
        self.connection = Connection()
        connection_response = await self.connection.connect()
        self.update.emit(connection_response)
        writer_future = asyncio.ensure_future(self.write_loop())
        reader_future = asyncio.ensure_future(self.connection.ws_reader())
        await asyncio.wait([writer_future, reader_future], return_when=asyncio.FIRST_COMPLETED)

    async def write_loop(self):
        while True:
            try:
                print("abcd")
                message = self.req_queue.get()
                response = await self.connection.ws_writer(message)
                self.update.emit(response)
                print(response)
            except queue.Empty:
                pass
