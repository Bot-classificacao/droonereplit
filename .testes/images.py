
import os
import sys

# Adiciona o diretório 'services' ao sys.path
sys.path.append(os.path.join(os.getcwd()))

# Agora você pode importar os módulos
from services.connection import conectar
from services.utils import image_save, image_to_byte_array, image_update

host, user, password, schema = ''

def getImagesCount(id_cliente):
    cnx, cur = conectar(host, user, password, schema)
    cur = cnx.cursor()

    cur.execute("SELECT count(*) FROM tbl_imagens WHERE id_cliente = %s AND path LIKE '%Não Autorizado%'", (id_cliente, ))
    cnx.commit()
    desconectar(cnx, cur)
    return cur.fetchall()