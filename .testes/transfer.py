

import sqlite3
import mysql.connector

from services.connection import conectar

# Conectar ao banco de dados SQLite
conn_sqlite = sqlite3.connect('test.db')
cursor_sqlite = conn_sqlite.cursor()

# Executar SELECT na tabela tbl_users do SQLite
cursor_sqlite.execute("SELECT * FROM tbl_users")
users = cursor_sqlite.fetchall()

# Obter informações sobre as colunas
cursor_sqlite.execute("PRAGMA table_info(tbl_users)")
columns = [column[1] for column in cursor_sqlite.fetchall()]

# Fechar conexão com SQLite
conn_sqlite.close()

# Conectar ao banco de dados MySQL
conn_mysql = mysql.connector.connect(
    host='srv720.hstgr.io',
    user='u611546537_DBA_Droone',
    password='S3nh@FOrt3DBA_DrOOne_2024###',
    database='u611546537_Droone'
)
cursor_mysql = conn_mysql.cursor()


# Criar a tabela tbl_users no MySQL (se não existir)
create_table_query = f"CREATE TABLE IF NOT EXISTS tbl_users ({', '.join([f'{col} TEXT' for col in columns])})"
cursor_mysql.execute(create_table_query)

# Inserir dados na tabela tbl_users do MySQL
insert_query = f"INSERT INTO tbl_users ({', '.join(columns)}) VALUES ({', '.join(['%s' for _ in columns])})"
cursor_mysql.executemany(insert_query, users)

# Commit das alterações e fechar conexão com MySQL
conn_mysql.commit()
conn_mysql.close()

print("Transferência de dados concluída com sucesso!")
