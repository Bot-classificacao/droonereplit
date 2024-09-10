import sqlite3
import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

from services.connection import get_connection
from model.user import User_create
from services.site import auth_db as auth


DATABASE_URL = 'test.db'

def get_connection():
    conn = sqlite3.connect(DATABASE_URL, check_same_thread=False)
    return conn

conn = get_connection()
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS tbl_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')
conn.commit()

username = 'userfaada_123'
email = 'emailfaada123@gmail.com'
password = 'SenhaFoda1!'

user = User_create(username=username, email=email, password=password)

async def register_user():
    await auth.register(user)

asyncio.run(register_user())

cursor.execute('SELECT password FROM tbl_users WHERE email = ?', (email,))
stored_password = cursor.fetchone()[0]
print(stored_password)

if stored_password != password:
    print('Senha armazenada como hash com sucesso.')
else:
    print('Falha: a senha está armazenada em texto plano.')