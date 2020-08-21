import asyncio
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime


class Backend:

    def __init__(self):
        """
        Used to connect to the database and create required tables if they don't exist yet.
        """
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.conn = sqlite3.connect('./db/historian.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.conn.execute('''CREATE TABLE IF NOT EXISTS request_history (
                      transaction_timestamp TIMESTAMP,
                      transaction_id INT,
                      unit_address INT,
                      function_code INT,
                      message_data BINARY,
                      PRIMARY KEY (transaction_timestamp));''')

        self.conn.commit()

        self.conn.execute('''CREATE TABLE IF NOT EXISTS response_history (
                      transaction_timestamp TIMESTAMP,
                      transaction_id INT,
                      unit_address INT,
                      function_code INT,
                      message_data BINARY,
                      PRIMARY KEY (transaction_timestamp));''')

        self.conn.commit()

    async def insert_request_history(self, transaction_id: int, unit_address: int, function_code: int,
                                     raw_request: bytes):
        """
        Inserts specified data into request history database table.

        Args:
            transaction_id (int): Unique ID of the transaction.
            unit_address (int): Address of the referenced unit.
            function_code (int): Unique function code.
            raw_request (bytes): Request data in bytes format.
        """
        await asyncio.get_event_loop().run_in_executor(self.executor, lambda: self._ext_execute_insert_query(
            'INSERT INTO request_history VALUES (?, ?, ?, ?, ?);',
            (
                datetime.now(),
                transaction_id,
                unit_address,
                function_code,
                raw_request)))

    async def insert_response_history(self, transaction_id: int, unit_address: int, function_code: int,
                                      raw_response: bytes):
        """
        Inserts specified data into response history database table.

        Args:
            transaction_id (int): Unique ID of the transaction.
            unit_address (int): Address of the referenced unit.
            function_code (int): Unique function code.
            raw_response (bytes): Request data in bytes format.
        """
        await asyncio.get_event_loop().run_in_executor(self.executor, lambda: self._ext_execute_insert_query(
            'INSERT INTO response_history VALUES (?, ?, ?, ?, ?);',
            (
                datetime.now(),
                transaction_id,
                unit_address,
                function_code,
                raw_response)))

    async def get_request_history(self) -> list:
        """
        Fetches request history data from the database.

        Returns:
            rows (list): Rows of the request history table.
        """
        return await asyncio.get_event_loop().run_in_executor(self.executor,
                                                              lambda: self._ext_execute_select_query(
                                                                  '''SELECT * FROM request_history ORDER BY  transaction_timestamp'''))

    async def get_response_history(self) -> list:
        """
        Fetches response history data from the database.

        Returns:
            rows (list): Rows of the response history table.
        """
        return await asyncio.get_event_loop().run_in_executor(self.executor,
                                                              lambda: self._ext_execute_select_query(
                                                                  '''SELECT * FROM response_history ORDER BY  transaction_timestamp'''))

    def _ext_execute_insert_query(self, query, values):
        self.cursor.execute(query, values)
        self.conn.commit()

    def _ext_execute_select_query(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    async def close(self):
        """
        Closes the database connection.
        """
        await asyncio.get_event_loop().run_in_executor(self.executor, lambda: self.conn.close())
