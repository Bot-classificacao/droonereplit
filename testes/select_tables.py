import sqlite3

DATABASE_URL = 'test.db'


def get_connection():
    conn = sqlite3.connect(DATABASE_URL, check_same_thread=False)
    return conn


conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

tables = cursor.fetchall()

for table in tables:
    print(table[0])

conn.close()
