import sys
import os

# Adicione o diretório raiz do projeto ao sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(_file_))))

from services.connection import setup_database, conectar, desconectar, host, user, password, schema

# Setup do banco de dados
setup_database()

# Conectar ao banco de dados MySQL
cnx, cur = conectar(host, user, password, schema)

# Verificar se um circuito já existe
def circuito_existe(email_circuito):
    try:
        SELECT = f"SELECT COUNT(*) FROM tbl_circuitos WHERE email_circuito = '{email_circuito}'"
        print(f"Executando consulta: {SELECT}")
        cur.execute(SELECT)
        count = cur.fetchone()[0]
        print(f"Resultado da consulta: {count}")
        return count > 0
    except Exception as e:
        print(f"Erro ao verificar circuito: {e}")
        return False

# Inserir um circuito
def insertCirc(id_cliente, email_circuito, descricao, status):
    try:
        existe = circuito_existe(email_circuito)
        print(f"Circuito existe antes da inserção: {existe}")
        if not existe:
            INSERT = f"""
            INSERT INTO tbl_circuitos(id_cliente,email_circuito,descricao,status) VALUES
            ('{id_cliente}','{email_circuito}','{descricao}','{status}')
            """
            print(f"Executando inserção: {INSERT}")
            cur.execute(INSERT)
            cnx.commit()
            print('Insert realizado com sucesso...')
        else:
            print(f'O circuito com o email {email_circuito} já existe.')
    except Exception as e:
        print(f"Erro ao inserir circuito: {e}")
        cnx.rollback()

# Testar a inserção do circuito com um email diferente
email_teste = 'teste_unique@example.com'
print(f"Circuito existe antes da inserção: {circuito_existe(email_teste)}")
insertCirc(1, email_teste, 'TESTE', 'ativo')
print(f"Circuito existe após a inserção: {circuito_existe(email_teste)}")

# Desconectar do banco de dados
desconectar(cnx, cur)