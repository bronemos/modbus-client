import sqlite3
from datetime import datetime


class Backend:

    def __init__(self):
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

    def insert_request_history(self, response):
        self.cursor.execute('''INSERT INTO request_history
                        VALUES (?, ?, ?, ?, ?);''',
                            (datetime.now(), response['transaction_id'], response['unit_address'],
                             response['function_code'], response['raw_request']))
        self.conn.commit()

    def insert_response_history(self, response):
        self.cursor.execute('''INSERT INTO response_history 
                        VALUES (?, ?, ?, ?, ?);''',
                            (datetime.now(), response['transaction_id'], response['unit_address'],
                             response['function_code'], response['raw_data']))
        self.conn.commit()

    def get_request_history(self):
        self.cursor.execute('''SELECT * FROM request_history ORDER BY  transaction_timestamp DESC LIMIT 150''')
        return self.cursor.fetchall()

    def get_response_history(self):
        self.cursor.execute('''SELECT * FROM response_history ORDER BY  transaction_timestamp DESC LIMIT 150''')
        return self.cursor.fetchall()
