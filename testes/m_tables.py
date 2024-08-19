import sys
import os

# Adicione o diretório raiz do projeto ao sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.connection import setup_database, conectar, desconectar, host, user, password, schema

# Setup do banco de dados
setup_database()

# Conectar ao banco de dados MySQL
cnx, cur = conectar(host, user, password, schema)

# Executar um SELECT de todas as tabelas existentes
try:
    cur.execute('SHOW TABLES')
    tabelas = cur.fetchall()
    print("Tabelas existentes no banco de dados:")
    for tabela in tabelas:
        print(tabela[0])
except Exception as e:
    print(f"Erro ao listar as tabelas: {e}")

# Desconectar do banco de dados
desconectar(cnx, cur)
