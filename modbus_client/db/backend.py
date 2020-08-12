import sqlite3
from datetime import datetime


class Backend:

    def __init__(self):
        """
        Used to connect to the database and create required tables if they don't exist yet.
        """
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

    def insert_request_history(self, transaction_id: int, unit_address: int, function_code: int, raw_request: bytes):
        """
        Inserts specified data into request history database table.

        Args:
            transaction_id (int): Unique ID of the transaction.
            unit_address (int): Address of the referenced unit.
            function_code (int): Unique function code.
            raw_request (bytes): Request data in bytes format.
        """
        self.cursor.execute('''INSERT INTO request_history
                        VALUES (?, ?, ?, ?, ?);''',
                            (datetime.now(), transaction_id, unit_address, function_code, raw_request))
        self.conn.commit()

    def insert_response_history(self, transaction_id: int, unit_address: int, function_code: int, raw_response: bytes):
        """
        Inserts specified data into response history database table.

        Args:
            transaction_id (int): Unique ID of the transaction.
            unit_address (int): Address of the referenced unit.
            function_code (int): Unique function code.
            raw_response (bytes): Request data in bytes format.
        """
        self.cursor.execute('''INSERT INTO response_history 
                        VALUES (?, ?, ?, ?, ?);''',
                            (datetime.now(), transaction_id, unit_address,
                             function_code, raw_response))
        self.conn.commit()

    def get_request_history(self) -> list:
        """
        Fetches request history data from the database.

        Returns:
            rows (list): Rows of the request history table.
        """
        self.cursor.execute('''SELECT * FROM request_history ORDER BY  transaction_timestamp LIMIT 150''')
        return self.cursor.fetchall()

    def get_response_history(self) -> list:
        """
        Fetches response history data from the database.

        Returns:
            rows (list): Rows of the response history table.
        """
        self.cursor.execute('''SELECT * FROM response_history ORDER BY  transaction_timestamp LIMIT 150''')
        return self.cursor.fetchall()
