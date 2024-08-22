from send_alerts.sender_mail import message_send

from send_alerts.send_web_whats.send_web_whats import DrooneSend


def enviar_alerta_whatsapp(fone, mensagem):
    DrooneSend().send_message(fone, mensagem)


def enviar_alerta_email(para, assunto, mensagem, caminho_imagem = None):
    print('Função ALERTA EMAIL recebida', caminho_imagem)
    message_send(para, assunto, mensagem, caminho_imagem)
