from datetime import datetime

from services.connection import conectar, desconectar

data_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# insere um circuito
def insertCirc(id_cliente, email_circuito, nome_dispositivo, status):
    INSERT = f"""
    INSERT INTO Circuitos(id_cliente,email_circuito,nome_dispositivo,status)VALUES
    ('{id_cliente}','{email_circuito}','{nome_dispositivo}','{status}')
    """
    cur.execute(INSERT)
    cnx.commit()
    print('Insert realizado com sucesso...')


# insere uma camera
def insertCam(cur, cnx, id_circuito, localizacao):
    INSERT = f"""
    INSERT INTO Cameras (id_circuito,localizacao,status) VALUES
    ({id_circuito},'{localizacao}','ativo');
    """
    cur.execute(INSERT)
    cnx.commit()
    print('Insert realizado com sucesso...')


# insere na fila de processamento (tabela imagens)
def insertImage(cnx, cur, data_hora_chegada: str, full_path: str,
                status_imagem: str, id_cliente: int, id_circuito: int,
                id_camera: int):
    print(f'{data_now},{data_hora_chegada},{full_path},{status_imagem},{id_cliente},{id_circuito},{id_camera}')
    INSERT = f"""
        INSERT INTO Imagens
        (Timestamp_Criacao,Data_Hora_Chegada,Full_Path,Status_Imagem,id_cliente,id_circuito,id_camera) VALUES 
        ('{data_now}','{data_hora_chegada}','{full_path}','{status_imagem}',{id_cliente},{id_circuito},{id_camera})
    """

    cur.execute(INSERT)
    cnx.commit()
    print('Insert realizado com sucesso...')


# pega a localizacao da camera
def isLocCamera(cur, id_circuito):
    SELECT = f"""
    SELECT localizacao FROM Cameras 
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
    SELECT id_camera FROM Cameras 
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
    SELECT id_circuito FROM Circuitos 
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
    SELECT cd.id_cliente,ct.id_circuito FROM   Circuitos ct INNER JOIN Clientes_Droone cd
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
    SELECT numero FROM whatsapp w INNER JOIN Clientes_Droone cd 
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
    select e.email from Clientes_Droone c inner join emails_clientes e on e.email_id = c.email where c.id_cliente = {id_cliente};
    """
    cur.execute(SELECT)
    email_circuito = cur.fetchone()
    if isinstance(email_circuito, tuple):
        return email_circuito[0]
    return (None, None)
