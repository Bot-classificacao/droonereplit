from .constantes import HOST, USUARIO, SENHA, NAME, PORTA

from services.connection import conectar, desconectar

msg_alerta_amarelo = '''
    *Atenção*, notamos uma movimentação em suas camêras, por favor verifique-as\n
    Alerta : *Amarelo*
    '''
msg_alerta_vermelho = '''
    *Atenção-Urgente*, notamos uma movimentação em suas camêras, por favor verifique-as\n
    Alerta : *Vermelho*
    '''


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


def is_number_cliente(cur, id_cliente):
    SELECT = f"""SELECT numero FROM whatsapp w INNER JOIN Clientes_Droone cd 
    ON w.whats_id = cd.whatsapp
    WHERE cd.id_cliente = '{
        id_cliente}'"""
    cur.execute(SELECT)
    whatsapp = cur.fetchall()
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
