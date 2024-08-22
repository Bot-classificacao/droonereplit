from services.connection import conectar, desconectar

import datetime
from datetime import datetime
import os
import mysql.connector
import sys

sys.path.append(os.getcwd())
from constantes import HOST, USUARIO, SENHA, NAME, PORTA

# pega a data hora atual
data_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
msg_alerta_amarelo = '''
    *Atenção*, notamos uma movimentação em suas camêras, por favor verifique-as\n
    Alerta : *Amarelo*
    '''
msg_alerta_vermelho = '''
    *Atenção-Urgente*, notamos uma movimentação em suas camêras, por favor verifique-as\n
    Alerta : *Vermelho*
    '''
# print(data_now)
# insere um circuito


def insert_circuito(id_cliente, email_circuito, nome_dispositivo, status):
    cnx, cur = conectar(HOST, USUARIO, SENHA, NAME)
    INSERT = f"""
    INSERT INTO Circuitos(id_cliente,email_circuito,nome_dispositivo,status)VALUES
    ('{id_cliente}','{email_circuito}','{nome_dispositivo}','{status}')
    """
    cur.execute(INSERT)
    cnx.commit()
    desconectar(cnx, cur)
    print('Insert realizado com sucesso...')


# insere uma camera
def insert_camera(cur, cnx, id_circuito, localizacao, status='ativo'):
    INSERT = f"""
    INSERT INTO Cameras
    (id_circuito,localizacao,status)VALUES
    ('{id_circuito}','{localizacao}','{status}')
    """
    cur.execute(INSERT)
    cnx.commit()
    print('Insert realizado com sucesso...')


# insere na fila de processamento (tabela imagens)


def insert_file_process(cnx, cur, data_hora_chegada, full_path, status_imagem,
                        id_cliente, id_circuito, id_camera):
    try:
        # Certifique-se de que todos os resultados anteriores foram lidos
        if cur.with_rows:
            cur.fetchall()
        INSERT = f"""
            INSERT INTO Imagens
            (Timestamp_Criacao,Data_Hora_Chegada,Full_Path,Status_Imagem,id_cliente,id_circuito,id_camera) VALUES
            ('{data_now}','{data_hora_chegada}','{full_path}','{status_imagem}',{id_cliente},{id_circuito},{id_camera});
        """

        cur.execute(INSERT)
        cnx.commit()
        print('Insert realizado com sucesso...')
    except mysql.connector.errors as e:
        print(e)


# pega a localizacao da camera


def eh_loc_cam(cur, id_circuito):
    SELECT = f"""
    SELECT localizacao FROM Cameras
    WHERE status = 'ativo' AND id_circuito ={id_circuito}
    """
    cur.execute(SELECT)
    loc = cur.fetchone()
    if isinstance(loc, tuple):
        return loc[0]
    return (None, None)


# pega a id da camera


def eh_id_cam(cur, id_circuito):
    SELECT = f"""
    SELECT id_camera FROM Cameras
    WHERE status = 'ativo' AND id_circuito ={id_circuito}
    """
    cur.execute(SELECT)
    id_cam = cur.fetchone()
    if isinstance(id_cam, tuple):
        return id_cam[0]
    return None


# pega o Id do circuito


def eh_id_circuito(cur, id_cliente, IP_principal):
    SELECT = f"""
    SELECT id_circuito FROM Circuitos
    WHERE status = 'ativo' AND id_cliente ={id_cliente} AND IP_principal = '{IP_principal}'
    """
    cur.execute(SELECT)
    id_circuito = cur.fetchone()
    if isinstance(id_circuito, tuple):
        return id_circuito[0]
    return None


# pega o Id do cliente


def eh_valid_client(cur, sender_email_recebido):
    SELECT = f"""
    SELECT cd.id_cliente,ct.id_circuito FROM   Circuitos ct INNER JOIN Clientes_Droone cd
    ON cd.id_cliente = ct.id_cliente
    WHERE ct.email_circuito = '{sender_email_recebido}' and cd.status = 'ativo';
    """
    cur.execute(SELECT)
    id_cliente = cur.fetchone()
    if isinstance(id_cliente, tuple):
        return id_cliente[0], id_cliente[1]
    return (None, None)


def ids_alert_vermelho(cur):
    SELECT = "SELECT id_cliente FROM Alerta WHERE status = 'vermelho' "
    cur.execute(SELECT)
    id_cliente = cur.fetchall()
    print(id_cliente)
    lista_ids = []
    for ids in id_cliente:
        if isinstance(ids, tuple):
            lista_ids.append(ids[0])
    return lista_ids


def ids_alert_amarelo(cur):
    SELECT = """SELECT id_cliente FROM Alerta WHERE status = 'amarelo' """
    cur.execute(SELECT)
    id_cliente = cur.fetchall()
    print(id_cliente)
    lista_ids = []
    for ids in id_cliente:
        if isinstance(ids, tuple):
            lista_ids.append(ids[0])
    return lista_ids


def is_whatsapp_cliente(cur, id_cliente):
    SELECT = f"""SELECT numero FROM whatsapp w INNER JOIN Clientes_Droone cd 
    ON w.whats_id = cd.whatsapp
    WHERE cd.id_cliente = '{
        id_cliente}'"""
    cur.execute(SELECT)
    whatsapp = cur.fetchone()
    print(whatsapp)
    if isinstance(whatsapp, tuple):
        return whatsapp[0]
    return None


def is_mail_cliente(cur, id_cliente):
    SELECT = f"""SELECT e.email FROM emails_clientes e INNER JOIN Clientes_Droone cd
    ON e.email_id = cd.email
    WHERE id_cliente = '{
        id_cliente}'"""
    cur.execute(SELECT)
    email_cliente = cur.fetchone()
    print(email_cliente)
    if isinstance(email_cliente, tuple):
        return email_cliente[0]
    return None
