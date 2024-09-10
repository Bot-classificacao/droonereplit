from PIL import Image
import io
import os

from services.connection import conectar


def image_to_byte_array(image_path):
    with Image.open(image_path) as img:
        byte_arr = io.BytesIO()
        ext = os.path.splitext(image_path)[1].lower()
        format = 'JPEG' if ext in ['.jpeg', '.jpg'] else 'PNG'
        img.save(byte_arr, format=format)
        print("Imagem convertida para byte array.")
        return byte_arr.getvalue()

# Ta faltando o full path antigo, doidao
def image_update(image_path):
    cnx, cur = conectar()
    UPDATE = f"""
    UPDATE tbl_imagens SET path = '{full_path}' WHERE path LIKE '{full_path}'
    """
    cur.execute(UPDATE)
    cnx.commit()
    desconectar(cnx, cur)
    print(f"Imagem atualizada no banco de dados")

def image_save(blob, full_path):
    cnx, cur = conectar()
    UPDATE = f"""
    UPDATE tbl_imagens SET blob_imagens = '{blob}' WHERE path LIKE '{full_path}'
    """
    cur.execute(UPDATE)
    cnx.commit()
    desconectar(cnx, cur)
    print(f"Blob salvo no banco de dados")
