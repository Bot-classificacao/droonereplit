import asyncio
import imaplib
import os
import time
from imap_tools.query import OR
from send_alerts.send_with_api import postar
from send_alerts.verify_bd import *
from services.alerts import enviar_alerta_email as enviar_alerta_email
from services.alerts import enviar_alerta_whatsapp as enviar_alerta_whatsapp

from services.classificador.classifier_alert_report import carregar_ou_treinar_modelo, processar_nova_imagem
from services.connection import conectar, desconectar, insert_image

from imap_tools import MailBox, AND
from constantes import *
from services.feedback.uteis_mail import apply_images, get_image_id_by_date, update_image_by_id


async def count_mail() -> int:
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
        msgs = sorted(msgs, key=lambda x: x.date, reverse=True)
        inbox_mail = []
        # Acesse o e-mail mais recente
        if msgs:  # verifica se encontrou e-mails
            for msg in msgs:
                inbox_mail.append(msg)
        if len(inbox_mail) > 0:
            return len(inbox_mail)
        else:
            return 0


async def get_mail() -> dict:
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
            # msgs = sorted(msgs, reverse=True, key=lambda x: x.date)
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


async def filter_mail(txt: str):
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


# 06-09 Fioruci refatorando
async def classify_email():
    while True:
        print("Loop ta rodando")
        list_mails = await count_mail()
        print(f'mensagens não lidas : {list_mails}')
        for iterator in range(list_mails):
            email = await get_mail()
            print("Email pego")
            cnx, cur = None, None
            if email:
                try:
                    cnx, cur = conectar()
                    print("Filtrando o email")
                    dic_body = await filter_mail(email['body'])
                    if not dic_body:
                        raise ValueError(
                            "filtra_email retornou um dicionário vazio")
                    print(f"dic_body: {dic_body}")

                    # verifica o status a partir da lista (email['filename']) -> retorna o dicionario ['path'] e ['status']
                    # Obs: ainda em teste favor nn alterar por enquanto
                    result = apply_images(email)
                    path_str = result.get('path')
                    status = result.get('status')
                    print(f"""
                    path_str: {path_str}
                    status : {status}
                    """)

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
                            ass = f"""                           
                            <p>Alerta de segurança: Acesso cameras detectaram uma movimentação.</p>
                            <p>Cliente:    {email_cliente}</p>
                            <p>Circuito: {end_ip}</p>
                            <p>Camêra: {dispositivo}</p>
                            """
                            whats_msg = f"Alerta de segurança: Acesso cameras detectaram uma movimentação.\nCliente:    {email_cliente}\nCircuito: {end_ip}\nCamêra: {dispositivo}"

                            if whatsapp != None:
                                postar(whatsapp, whats_msg, email['date'])
                            if email_cliente != None:
                                enviar_alerta_email(
                                    email_cliente,
                                    'ALERTA -DROONE - VJBOTS', ass,
                                    os.path.join(BASE_PATH_IMG, path_files))
                            print("email: ", email_cliente, "\nwhatsapp: ",
                                  whatsapp)
                            if "Não há anexo" not in path_files:
                                modelo = carregar_ou_treinar_modelo()
                                print("Classificando imagem")
                                for filename in email['filename']:
                                    path_full_img = os.path.join(
                                        BASE_PATH_IMG, filename)
                                    print(
                                        f"Processando imagem: {path_full_img}")
                                    processar_nova_imagem(
                                        path_full_img, modelo, email_cliente,
                                        whatsapp, email['date'])
                                    # pega a imagem inserida agora
                                    id_image = get_image_id_by_date(
                                        date=email['date'])
                                    # da um update no campo status
                                    update_image_by_id(id=id_image)
                            else:
                                print(
                                    "Erro ao inserir dados no banco de dados")

                    else:
                        print(
                            f"cliente não encontrado para o cliente em nossa base de dados"
                        )

                except ValueError as ve:
                    print(f"Erro de validação: {ve}")
                except Exception as e:
                    print(f"Erro inesperado ao processar o email: {e}")
                finally:
                    if cnx and cur:
                        desconectar(cnx, cur)
            else:
                print(
                    'Não há emails do @DVR!! por favor verifique a caixa de email'
                )
            print("Loop de emails finalizado")
            time.sleep(30)  # Espera 30 segundos antes de verificar novamente
        import random as rd
        sleep_seconds = rd.randrange(60, 120)
        await asyncio.sleep(round(sleep_seconds))


# Nova Função
async def processar_email_e_imagem():
    email = await get_mail()
    if email and 'filename' in email:
        for filename in email.get('filename', ()):
            image_path = os.path.join('classificador/classificadorIA/queue',
                                      filename)
            insert_image(image_path,
                         'Descrição opcional ou detalhes do e-mail')
            print(f"Imagem {filename} armazenada no banco de dados.")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(processar_email_e_imagem())
    loop.close()
