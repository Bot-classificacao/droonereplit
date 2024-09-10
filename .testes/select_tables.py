from mysql.connector import Error, errors
from mysql import connector
import sqlite3


def conectar():
    connection = None
    cursor = None
    try:
        print('MySQL')
        connection = connector.connect(host=host,
                                       user=user,
                                       password=password,
                                       database=schema,
                                       buffered=True)
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
    finally:
        return connection, cursor


# host = 'srv720.hstgr.io'
# user = 'u611546537_DBA_Droone'
# password = 'S3nh@FOrt3DBA_DrOOne_2024###'
# schema = 'u611546537_Droone'
# port = '3306'

# cnx, cur = conectar(host, user, password, schema)
# cursor = cnx.cursor() if cnx else None

# URL de conexão
DATABASE_URL = "test.db"


# Conectando com a database
def get_connection():
    conn = sqlite3.connect(DATABASE_URL, check_same_thread=False)
    return conn


cnx = get_connection()
cursor = cnx.cursor()

# def convert_to_blob(file_path):
#     with open(file_path, "rb") as file:
#         blob_data = file.read()
#     return blob_data

# blob_img = convert_to_blob('classificador/classificadorIA/classificados/Não Autorizado/ch04_20240814_190409_E.jpg')

# # Use a consulta parametrizada para evitar erros de sintaxe
# query = "UPDATE tbl_imagens SET path = %s, blob_imagens = %s WHERE id_imagem = %s"
# params = ('classificador/classificadorIA/classificados/Não Autorizado/ch04_20240814_190409_E.jpg', blob_img, 1242)

# cursor.execute(query, params)
# cnx.commit()

# cursor.execute("SHOW COLUMNS FROM Imagens")
# cnx.commit()
# cursor.execute("select * from tbl_imagens WHERE id_imagem = 1242")

# from passlib.context import CryptContext

# # cnx.close()
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def get_password_hash(password):
#     return pwd_context.hash(password)
# hashed = get_password_hash('admin')

# # cursor.execute("SELECT * from tbl_clientmails where email = 'validandohj@gmail.com'")
# cursor.execute("UPDATE tbl_users SET email = 'validandohj@gmail.com', password = ? WHERE id = 13", (hashed,))
# # cursor.execute("SELECT * from tbl_clientes")

cnx.commit()
cursor.execute("SELECT * FROM Users")

for user in users:
    query = "INSERT INTO tbl_users (name, email, password) VALUES (%s, %s, %s)"
tables = cursor.fetchall()

for table in tables:
    print(table)

cnx.close()
