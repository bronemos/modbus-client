import asyncio
import queue
import sqlite3
from datetime import datetime
from queue import Queue
from threading import Thread

from PySide2.QtCore import QObject, Signal

from modbus_client.communication.connection import Connection

from concurrent.futures import ThreadPoolExecutor


class StateManager(QObject):
    executor = ThreadPoolExecutor(max_workers=1)
    update = Signal(dict)
    current_state = dict()
    update_counter = Signal(int)
    update_view = Signal()

    def __init__(self):
        super(StateManager, self).__init__()
        self.req_queue = Queue()
        self.db_conn = sqlite3.connect('./db/historian.db', check_same_thread=False)
        self.db = self.db_conn.cursor()

    def run_loop(self):
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
                await self.connection.session.close()
                return
            print(message)
            response = await self.connection.ws_writer(message)
            print(response['raw_data'])
            print(response['raw_request'])
            if response['transaction_id'] >= 128:
                try:
                    self.db.execute('''INSERT INTO response_history 
                                    VALUES (?, ?, ?, ?, ?);''',
                                    (datetime.now(), response['transaction_id'], response['unit_address'],
                                     response['function_code'], response['raw_data']))
                    self.db_conn.commit()
                    self.db.execute('''INSERT INTO request_history
                                    VALUES (?, ?, ?, ?, ?);''',
                                    (datetime.now(), response['transaction_id'], response['unit_address'],
                                     response['function_code'], response['raw_request']))
                    self.db_conn.commit()
                    print('inserted successfully')
                except Exception as e:
                    print(e)
            self.update.emit(response)

    async def counter(self):
        while True:
            for i in range(1, 101):
                await asyncio.sleep(0.03)
                self.update_counter.emit(i)
            self.update_view.emit()

    def _ext_get_message(self):
        return self.req_queue.get()
