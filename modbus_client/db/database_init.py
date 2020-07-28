import sqlite3

conn = sqlite3.connect('historian.db')

db = conn.cursor()

db.execute('''CREATE TABLE request_history (
              transaction_timestamp TIMESTAMP,
              transaction_id INT,
              unit_address INT,
              function_code INT,
              message_data BINARY,
              PRIMARY KEY (transaction_id));''')

db.execute('''CREATE TABLE response_history (
              transaction_timestamp TIMESTAMP,
              transaction_id INT,
              unit_address INT,
              function_code INT,
              message_data BINARY,
              PRIMARY KEY (transaction_id));''')

conn.commit()

conn.close()
