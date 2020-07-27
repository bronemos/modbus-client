import sqlite3

conn = sqlite3.connect('historian.db')

db = conn.cursor()

db.execute('''CREATE TABLE ''')