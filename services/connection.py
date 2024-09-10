import os
import sqlite3
from mysql.connector import Error, errors

from dotenv import load_dotenv
from fastapi import HTTPException
from mysql import connector

# IMPLEMENTAÇÃO CONN - MYSQL / POSTGRES

HOST = 'srv720.hstgr.io'
USER = 'u611546537_DBA_Droone'
PASSWORD = 'S3nh@FOrt3DBA_DrOOne_2024###'
SCHEMA = 'u611546537_Droone'


def conectar():
    try:
        print('MySQL')
        connection = connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=SCHEMA,
        )
        print(connection)
        if connection.is_connected():
            cursor = connection.cursor(buffered=True)
            cursor.execute('select database()')
            banco_de_dados = cursor.fetchone()
            try:
                if banco_de_dados:
                    print('conectado com sucesso ao Banco de Dados')
                    return connection, cursor
            except Exception as e:
                print('Connection successful, but no database found.', e)
        else:
            print("Connection failed.")
    except errors.DatabaseError as err:
        print(f"Erro ao conectar ao MySQL: {err}")
        return None


def desconectar(connection, cursor) -> bool:
    if connection is not None:
        if cursor:
            cursor.close()
        connection.close()
        print('Connection closed...')
    return not connection.is_connected() if connection else True


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
    # TODO - Teste de conexão com o MySQL

    conn = get_connection()
    try:

        cursor = conn.cursor()  # Setup Database deveria garantir o ACT
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tbl_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT
        )
        ''')  # Criação da Tabela tbl_users
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tbl_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            token TEXT,
            default INTEGER DEFAULT 0
        )
        ''')  # Criação da Tabela tokens
        conn.commit()
        cursor.close()
        return {"message": "Database setada com sucesso."}
    except Exception as e:
        # Mensagem de erro mais genérica
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao configurar o banco de dados: {str(e)}") from e
    finally:
        conn.close()


# main garante que o banco de dados seja criado -> connection garante cur, cnx
# Nova função
def insert_image(image_path, description):
    connection, cursor = conectar()
    with open(image_path, "rb") as f:
        image_data = f.read()
    sql = "INSERT INTO images (image, description) VALUES (%s, %s)"
    cursor.execute(sql, (image_data, description)) if cursor else None
    conn[0].commit() if conn[0] else None
    if cursor:
        cursor.close()
    desconectar(conn, cursor)
    return image_data


def testes():
    setup_database()
