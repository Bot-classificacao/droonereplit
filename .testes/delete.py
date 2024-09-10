import sys
import os
# Adicione o diretório raiz do projeto ao sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.connection import conectar

for i in range(40):
  cnx, cur = conectar()
  query = "DELETE FROM tbl_users WHERE id_user = %s"
  cur.execute(query, (i, ))
  cnx.commit()
  print(f"Deletando ID: {i}")