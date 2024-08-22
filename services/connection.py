import os
import sqlite3
from mysql.connector import errors, errorcode

from dotenv import load_dotenv
from fastapi import HTTPException
from mysql import connector

# IMPLEMENTAÇÃO CONN - MYSQL / POSTGRES

host = 'srv720.hstgr.io'
user = 'u611546537_DBA_Droone'
password = 'S3nh@FOrt3DBA_DrOOne_2024###'
schema = 'u611546537_Droone'
port = '3306'


def conectar(host, user, password, schema):
    connection = None
    cursor = None
    try:
        print('MySQL')
        connection = connector.connect(
            host=host,
            user=user,
            password=password,
            database=schema,
        )
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute('select database()')
            banco_de_dados = cursor.fetchone()
            if banco_de_dados:
                print(
                    f'conectado com sucesso ao Banco de Dados {banco_de_dados[0]}'
                )
            else:
                print('Connection successful, but no database found.')
            return connection, cursor
        else:
            print("Connection failed.")

    except mysql.connector.errors.Error as err:
        raise Exception('Erro: ', err) from err
    finally:
        return connection, cursor


def desconectar(connection, cursor) -> bool:
    if connection is not None:
        if cursor:
            cursor.close()
        connection.close()
        print('Conection closed...')
    return not connection.is_connected()


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
    #cursor, connection = conectar(host, user, password, schema)
    # TODO - Teste de conexão com o MySQL

    conn = get_connection()
    try:

        cursor = conn.cursor()  # Setup Database deveria garantir o ACT
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT
        )
        ''')  # Criação da Tabela users
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
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


def testes():
    setup_database()
