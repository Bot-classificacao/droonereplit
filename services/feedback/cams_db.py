from datetime import datetime
import base64

from fastapi import HTTPException
from services.connection import conectar, desconectar

data_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

cnx, cur = conectar()
cur = cnx.cursor() if cnx else None


# insere um circuito
def insertCirc(id_cliente, email_circuito, nome_dispositivo, status):
    INSERT = f"""
    INSERT INTO tbl_circuitos(id_cliente,email_circuito,nome_dispositivo,status)VALUES
    ('{id_cliente}','{email_circuito}','{nome_dispositivo}','{status}')
    """
    cur.execute(INSERT)
    cnx.commit()
    print('Insert realizado com sucesso...')


# insere uma camera
def insertCam(cur, cnx, id_circuito, localizacao):
    INSERT = f"""
    INSERT INTO tbl_cameras (id_circuito,localizacao,status) VALUES
    ({id_circuito},'{localizacao}','ativo');
    """
    cur.execute(INSERT)
    cnx.commit()
    print('Insert realizado com sucesso...')


# insere na fila de processamento (tabela imagens)
def insertImage(cnx, cur, data_hora_chegada: str, full_path: str,
                status_imagem: str, id_cliente: int, id_circuito: int,
                id_camera: int):
    print(
        f'{data_now},{data_hora_chegada},{full_path},{status_imagem},{id_cliente},{id_circuito},{id_camera}'
    )
    INSERT = f"""
        INSERT INTO tbl_imagens
        (timestamp_create,datetime_chegada,path,status,id_cliente,id_circuito,id_camera) VALUES 
        ('{data_now}','{data_hora_chegada}','{full_path}','{status_imagem}',{id_cliente},{id_circuito},{id_camera})
    """

    cur.execute(INSERT)
    cnx.commit()
    print('Insert realizado com sucesso...')


# pega a imagem por usuario


def getImagesCount(id_usuario):
    # ,(id_cliente, )
    try:
        print(f"- COUNT ID USUARIO: {id_usuario}")
        cnx, cur = conectar()
        query = "SELECT COUNT(*) FROM tbl_imagens I INNER JOIN tbl_users U ON I.id_cliente = U.fk_cliente WHERE U.id_user = %s AND I.id_imagem NOT IN (SELECT F.image_id FROM tbl_feedbacks F)";
        print("Gettin count")
        cur.execute(query, (id_usuario, ))
        result = cur.fetchone()
        count = result[0] if result else 0
        return count

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter todos os IDs de feedback: {str(e)}")

    finally:
        if cnx:
            desconectar(cnx, cur)


def getImages(id_usuario):
    cnx = None
    cur = None
    try:
        cnx, cur = conectar()
        #  AND id_imagem NOT IN (SELECT F.image_id FROM Feedback F)
        print("Getting images")
        print(f"GETTIN IMG - ID CLIENTE: {id_usuario}")
        # id_cliente de imagens = fk_cliente de tbl_usuarios
        query = "SELECT I.blob_imagens, I.id_imagem FROM tbl_imagens I INNER JOIN tbl_users U ON I.id_cliente = U.fk_cliente WHERE U.id_user = %s AND I.id_imagem NOT IN (SELECT F.image_id FROM tbl_feedbacks F) LIMIT 1"
        cur.execute(query, (id_usuario, ))
        images = cur.fetchall()

        if not images:
            print("Nenhuma imagem encontrada para este usuário.")
            return []

        encoded_images = []
        for blob, id in images:
            if blob is not None:
                print(f"=== IMAGEM {id}")
                blob_final = base64.b64encode(blob).decode('utf-8')
                encoded_images.append((id, blob_final))

        return encoded_images

    except Exception as e:
        print(f"Erro ao obter imagens: {str(e)}")
        raise HTTPException(status_code=500,
                            detail=f"Erro ao obter imagens: {str(e)}")

    finally:
        if cnx and cur:
            desconectar(cnx, cur)


# pega a localizacao da camera
def isLocCamera(cur, id_circuito):
    SELECT = f"""
    SELECT localizacao FROM tbl_cameras 
    WHERE id_circuito ={id_circuito} 
    """
    cur.execute(SELECT)
    loc = cur.fetchone()
    if isinstance(loc, tuple):
        return loc[0]
    return (None, None)


# pega a id da camera
def isIdCamera(cur, id_circuito):
    SELECT = f"""
    SELECT id_camera FROM tbl_cameras 
    WHERE id_circuito = {id_circuito}
    """
    cur.execute(SELECT)
    id_cam = cur.fetchone()
    if isinstance(id_cam, tuple):
        return id_cam[0]
    return None


# pega o Id do circuito
def isCircuito(cur, id_cliente, IP_principal):
    SELECT = f"""
    SELECT id_circuito FROM tbl_circuitos 
    WHERE status = 'ativo' AND id_cliente ={id_cliente} AND IP_principal = '{IP_principal}'
    """
    cur.execute(SELECT)
    id_circuito = cur.fetchone()
    if isinstance(id_circuito, tuple):
        return id_circuito[0]
    return None


# pega o Id do cliente
def isClienteValid(cur, sender_email_recebido):
    SELECT = f"""
    SELECT cd.id_cliente,ct.id_circuito FROM tbl_circuitos ct INNER JOIN tbl_clientes cd
    ON cd.id_cliente = ct.id_cliente
    WHERE ct.email_circuito = '{sender_email_recebido}' and cd.status = 'ativo';
    """
    cur.execute(SELECT)
    id_cliente = cur.fetchone()
    if isinstance(id_cliente, tuple):
        return id_cliente[0], id_cliente[1]
    return (None, None)


def isWppCliente(cur, id_cliente):
    SELECT = f"""
    SELECT numero FROM tbl_whatsapps w INNER JOIN tbl_clientes cd 
    ON w.id = cd.whasapp
    WHERE cd.id_cliente = {id_cliente} AND cd.status = 'ativo'
    """
    cur.execute(SELECT)
    whatsapp = cur.fetchone()
    if isinstance(whatsapp, tuple):
        return whatsapp[0]
    return (None, None)


def isEmailCircuito(cur, id_cliente):
    SELECT = f"""
    select e.email from tbl_clientes c inner join tbl_clientmails e on e.email_id = c.email where c.id_cliente = {id_cliente};
    """
    cur.execute(SELECT)
    email_circuito = cur.fetchone()
    if isinstance(email_circuito, tuple):
        return email_circuito[0]
    return (None, None)


# services/feedback/cams_db.py


def remove_image_blob(image_id):
    try:
        cnx, cur = conectar()
        query = "UPDATE tbl_imagens SET blob_imagens = NULL WHERE id_imagem = %s"
        cur.execute(query, (image_id, ))
        cnx.commit()
        print(f"Blob removed for image ID: {image_id}")
    except Exception as e:
        print(f"Error removing image blob: {str(e)}")
    finally:
        desconectar(cnx, cur)
