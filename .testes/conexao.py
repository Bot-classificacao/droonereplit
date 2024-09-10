import os
import sqlite3
from mysql import connector


from dotenv import load_dotenv
from fastapi import HTTPException

# IMPLEMENTAÇÃO CONN - MYSQL / POSTGRES

load_dotenv()

variavel = 'eu'

host = os.getenv('HOST')
user = os.getenv('USUARIO')
password = os.getenv('SENHA')
schema = os.getenv('NAME')
port = os.getenv('PORTA')


def conectar(host, user, password, schema):
    connection = None
    cursor = None
    try:
        connection = connector.connect(
            host=host,
            user=user,
            password=password,
            database=schema,
            port=port
        )
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute('select database()')
            banco_de_dados = cursor.fetchone()
            print(f'MySQL - conectado com sucesso ao Banco de Dados {banco_de_dados[0]}')
            return connection, cursor
        else:
            print("Connection failed.")

    except mysql.connector.errorcode as err:
        raise Exception('Erro: ', err) from err
    finally:
        return connection, cursor


def desconectar(connection, cursor) -> bool:
    if connection.is_connected():
        if cursor:
            cursor.close()
        connection.close()
        print('Conection closed...')
    return True if connection == False else False










#SQLite

# URL de conexão
DATABASE_URL = "test.db"

# Conectando com a database
def get_connection():
    conn = sqlite3.connect(DATABASE_URL, check_same_thread=False)
    return conn

# Configuração do SQLite
def setup_database():
    print('SQLite')
    cursor, connection = conectar(host, user, password, schema)

    cur = cursor
    cnx = connection
    
    conn = get_connection()
    try:

        cursor = conn.cursor() # Setup Database deveria garantir o ACT
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tbl_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT
        )
        ''')  # Criação da Tabela users
        conn.commit()
        cursor.close()
        return {"message": "Tabela users criada com sucesso"}
    except Exception as e:
        # Mensagem de erro mais genérica
        raise HTTPException(status_code=500, detail=f"Erro ao configurar o banco de dados: {str(e)}") from e
    finally:
        conn.close()



def testes():
    setup_database()
