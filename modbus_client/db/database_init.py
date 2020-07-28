import sqlite3

conn = sqlite3.connect('historian.db')


conn.execute('''CREATE TABLE IF NOT EXISTS request_history (
              transaction_timestamp TIMESTAMP,
              transaction_id INT,
              unit_address INT,
              function_code INT,
              message_data BINARY,
              PRIMARY KEY (transaction_id));''')

conn.commit()

conn.execute('''CREATE TABLE IF NOT EXISTS response_history (
              transaction_timestamp TIMESTAMP,
              transaction_id INT,
              unit_address INT,
              function_code INT,
              message_data BINARY,
              PRIMARY KEY (transaction_id));''')

conn.commit()

conn.close()
