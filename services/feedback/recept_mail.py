import asyncio
import imaplib

from imap_tools.query import OR
from send_alerts.verify_bd import *
from services.alerts import enviar_alerta_email as enviar_alerta_email
from services.alerts import enviar_alerta_whatsapp as enviar_alerta_whatsapp

from services.classificador.classifier_alert_report import carregar_ou_treinar_modelo, processar_nova_imagem
from services.connection import conectar, desconectar

from imap_tools import MailBox, AND
from constantes import *


def get_imagem(att):
    print("Verificando anexo de imagem")
    queue_path = 'classificador\\classificadorIA\\queue'
    file_names = []
    if len(att) > 0:
        file_name = att.filename
        file_names.append(file_name)
        byte_img = att.payload
        with open(os.path.join(queue_path, file_name), 'wb') as anx:
            anx.write(byte_img)
        return file_names
    print("Nenhuma imagem encontrada")
    return None


def count_mail() -> int:
    # estrutura with para abrir e fechar email, e configs do email como caixa de msg, senha, usuario e servidor
    with MailBox('imap.hostinger.com',
                 993).login(username=mail_name_listener,
                            password=mail_pass_listener,
                            initial_folder='INBOX') as mailbox:
        # Busca tds os emails da pasta INBOX, caso esteja em spam add (.junk) dps de INBOX, ordenado por data mais recente
        msgs = mailbox.fetch(AND(subject='ALERTA DVR - Aclimacao Offices',
                                 seen=False),
                             charset='UTF-8',
                             reverse=True,
                             mark_seen=False)

        # ordena as mensagens
        # msgs = sorted(msgs, key=lambda x: x.date, reverse=True)
        inbox_mail = []
        # Acesse o e-mail mais recente
        if msgs:  # verifica se encontrou e-mails
            for msg in msgs:
                inbox_mail.append(msg)
        if len(inbox_mail) > 0:
            return len(inbox_mail)
        else:
            return 0


def get_mail() -> dict:
    print("Iniciando get_mail")
    try:
        # estrutura with para abrir e fechar email, e configs do email como caixa de msg, senha, usuario e servidor
        with MailBox('imap.hostinger.com',
                     993).login(username=mail_name_listener,
                                password=mail_pass_listener,
                                initial_folder='INBOX') as mailbox:
            # Busca tds os emails da pasta INBOX, caso esteja em spam add (.junk) dps de INBOX, ordenado por data mais recente

            msgs = mailbox.fetch(
                AND(subject='ALERTA DVR - Aclimacao Offices', seen=False),
                # reverse=True,
                charset='UTF-8',
                mark_seen=True)
            # ordena as mensagens
            msgs = sorted(msgs, reverse=True, key=lambda x: x.date)
            # Acesse o e-mail mais recente
            if msgs:  # verifica se encontrou e-mails
                for msg in msgs:
                    sender = msg.from_
                    subject = msg.subject

                    body = msg.text
                    date_mail = msg.date.strftime('%Y-%m-%d %H:%M:%S')
                    filenames = []
                    if len(msg.attachments) > 0:
                        for anexo in msg.attachments:
                            name_anexo = anexo.filename
                            filenames.append(name_anexo)
                            bytes_img = anexo.payload
                            # baixar a img
                            with open(
                                    f'classificador/classificadorIA/queue/{name_anexo}',
                                    'wb') as anx:
                                anx.write(bytes_img)
                    print("Retornando e-mail processado")
                    print("subject: ", subject)
                    email = {
                        'sender': sender,
                        'subject': subject,
                        'body': body,
                        'date': date_mail,
                        'filename': filenames,
                    }
                    # apaga o email apos ler e armazena-lo
                    mailbox.delete(msg.uid)
                    print("Email processado e deletado")
                    return email
            print("Nenhum e-mail com o assunto especificado encontrado")
    except Exception as e:
        print(f"Erro ao acessar o servidor de e-mail: {e}")
    return None


async def filtraEmail(txt: str):
    txt = txt.replace('\r', ' ')
    txt = txt.replace('\n', ' ')
    if 'término' in txt:
        frase_flag_alarme = 'Horário de término do alarme(D/M/A H:M:S): '
    else:
        frase_flag_alarme = 'Horário do inicio do alarme(D/M/A H:M:S): '

    pos_event = txt.find('Evento de alarme:') + len('Evento de alarme:')
    pos_canal = txt.find('Alarme no Canal No.:') + len('Alarme no Canal No.:')
    pos_nome = txt.find('Nome:') + len('Nome:')
    pos_time_alarme = txt.find(frase_flag_alarme) + len(frase_flag_alarme)
    pos_nome_disp = txt.find('Nome do dispositivo de alarme:') + \
        len('Nome do dispositivo de alarme:')
    pos_end = txt.find('End. IP DVR:') + len('End. IP DVR:')
    evento = txt[pos_event:pos_canal - len('Alarme no Canal No.:')]
    canal = txt[pos_canal:pos_nome - len('Nome:')]
    nome = txt[pos_nome:pos_time_alarme - len(frase_flag_alarme)]
    hora_alarme = txt[pos_time_alarme:pos_nome_disp -
                      len('Nome do dispositivo de alarme:')]
    dispositivo = txt[pos_nome_disp:pos_end - len('End. IP DVR:')]
    endereco = txt[pos_end:]
    return {
        'evento': evento.rstrip().lstrip(),
        'canal': canal.rstrip().lstrip(),
        'nome': nome.rstrip().lstrip(),
        'hora_alarme': hora_alarme.rstrip().lstrip(),
        'dispositivo': dispositivo.rstrip().lstrip(),
        'endereco': endereco.rstrip().lstrip(),
    }


async def classify_email():
    while True:
        print("Loop ta rodando")
        list_mails = count_mail()
        print(f'mensagens não lidas : {list_mails}')
        for iterator in range(list_mails):
            email = get_mail()
            print("Email pego")
            cnx, cur = None, None
            if email:
                try:
                    cnx, cur = conectar(HOST, USUARIO, SENHA, NAME)
                    print("Filtrando o email")
                    dic_body = await filtraEmail(email['body'])
                    if not dic_body:
                        raise ValueError(
                            "filtra_email retornou um dicionário vazio")
                    print(f"dic_body: {dic_body}")

                    path_files = ', '.join(
                        email['filename']
                    ) if email['filename'] else 'Não há anexo'
                    status_img = 'processada' if email[
                        'filename'] else 'a processar'
                    alerta_msg = f'''
                    <p>EMAIL DO CLIENTE: {email['sender']}</p>
                    <p>HORARIO DO EMAIL: {email['date']}</p>
                    <p>CAMINHO DO ARQUIVO: {path_files}</p>
                    <br>
                    <p>EVENTO: {dic_body['evento']}</p>
                    <p>CANAL: {dic_body['canal']}</p>
                    <p>NOME DA CAMERA: {dic_body['nome']}</p>
                    <p>HORA DO ALARME: {dic_body['hora_alarme']}</p>
                    <p>DISPOSITIVO: {dic_body['dispositivo']}</p>
                    <p>IP DO CIRCUITO: {dic_body['endereco']}</p>
                    '''
                    print(
                        alerta_msg.replace('<p>',
                                           '').replace('</p>',
                                                       '').replace('<br>', ''))
                    end_ip = dic_body['endereco']
                    dispositivo = dic_body['dispositivo']
                    sender_email = email['sender']
                    BASE_PATH_IMG = 'classificador/classificadorIA/queue/'

                    # valida cliente
                    id_cliente, id_circuito = eh_valid_client(
                        cur, sender_email)
                    if id_cliente is not None and id_circuito is not None:
                        print(
                            f"ID Circuito: {id_circuito}\nID Cliente: {id_cliente}"
                        )
                        if id_cliente is not None and id_circuito is not None:
                            id_cam = eh_id_cam(cur, id_circuito)
                            # Caso o id seja nulo ele insere ao db pois o cliente está em nossa base
                            if id_cam is None:
                                insert_camera(cur, cnx, id_circuito, end_ip)
                                id_cam = eh_id_cam(cur, id_circuito)
                            print("ID da camera: ", id_cam)
                        if (id_cliente is not None and id_circuito is not None
                                and id_cam is not None):
                            full_path = os.path.join(BASE_PATH_IMG, path_files)
                            insert_file_process(
                                cnx,
                                cur,
                                email["date"],
                                full_path,
                                status_img,
                                id_cliente,
                                id_circuito,
                                id_cam,
                            )
                            print(
                                "Dados inseridos na tabela de processamento!!!"
                            )
                            whatsapp = is_whatsapp_cliente(cur, id_cliente)
                            email_cliente = is_mail_cliente(cur, id_cliente)
                            print("email: ", email_cliente, "\nwhatsapp: ",
                                  whatsapp)
                            if "Não há anexo" not in path_files:
                                modelo = carregar_ou_treinar_modelo()
                                processar_nova_imagem(
                                    os.path.join(BASE_PATH_IMG,
                                                 path_files), modelo,
                                    email_cliente, whatsapp, email['date'])
                        else:
                            print("Erro ao inserir dados no banco de dados")
                    else:
                        print(
                            f"cliente não encontrado para o cliente em nossa base de dados"
                        )

                except Exception as e:
                    print(f"Erro ao processar o email: {e}")
                finally:
                    desconectar(cnx, cur)
            else:
                print(
                    'Não há emails do @DVR!! por favor verifique a caixa de email'
                )
            print("Loop de emails finalizado")
        import random as rd
        sleep_seconds = rd.randrange(60, 600)

        await asyncio.sleep(
            round(sleep_seconds)
        )  # Espera de 10 segundos antes de verificar novamente
