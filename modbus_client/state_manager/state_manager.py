import asyncio
import queue
import sqlite3
from datetime import datetime
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
        self.db_conn = sqlite3.connect('./db/historian.db')
        self.db = self.db_conn.cursor()
        self.update.emit(connection_response)
        writer_future = asyncio.ensure_future(self.write_loop())
        reader_future = asyncio.ensure_future(self.connection.ws_reader())
        await asyncio.wait([writer_future, reader_future], return_when=asyncio.FIRST_COMPLETED)
        writer_future.cancel()
        reader_future.cancel()

    async def write_loop(self):
        while True:
            try:
                message = self.req_queue.get()
                if message == 'DC':
                    await self.connection.session.close()
                    return
                print(message)
                response = await self.connection.ws_writer(message)
                print(type(response['raw_data']))
                try:
                    self.db.execute('''INSERT INTO response_history 
                                    VALUES (?, ?, ?, ?, ?);''',
                                    (datetime.now(), response['message_id'], response['unit_address'],
                                     response['function_code'], response['raw_data']))
                    self.db_conn.commit()
                    print("inserted successfully")
                except Exception as e:
                    print(e)
                self.update.emit(response)
            except queue.Empty:
                pass
