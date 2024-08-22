import sqlite3

DATABASE_URL = 'test.db'


def get_connection():
    conn = sqlite3.connect(DATABASE_URL, check_same_thread=False)
    return conn


conn = get_connection()
cursor = conn.cursor()

# cursor.execute(
#     'CREATE TABLE tokens (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, token TEXT, ja_usado INTEGER DEFAULT 0)'
# )
# cursor.execute('DELETE FROM tokens')
# conn.commit()

#cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
cursor.execute("SELECT * FROM users")

# cursor.execute("SELECT * FROM tokens")

tables = cursor.fetchall()

for table in tables:
    print(table)

user = cursor.fetchall()

for users in user:
    print(users)
conn.close()
