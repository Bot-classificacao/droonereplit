import datetime as dt
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from os.path import basename
from email import encoders
porta = 587
porta_hostiger = 465
host = 'smtp.gmail.com'
host_hostiger = ' smtp.hostinger.com'
my_mail = 'droone.server.0001@gmail.com'
my_key = 'c z h n h y x y x o e w r b k i'  #key do app google


def message_send(para, assunto, mensagem, files=None):
    msg = MIMEMultipart()
    msg['From'] = my_mail
    msg['To'] = para
    msg['Subject'] = assunto
    body = rf'''
    <p>{mensagem}</p>
    <p>Atts,</p>
    <p><b>Droone</b></p>
    <p><b>{dt.date.today()}</b></p>
    '''
    msg.attach(MIMEText(body, 'html'))
    if files != None:
        if isinstance(files, list):
            for file in files:
                arquivo = open(file, 'rb')
                att = MIMEBase('application', 'octet-stream')
                att.set_payload(arquivo.read())
                encoders.encode_base64(att)
                name_file = basename(file)
                print(name_file)
                att.add_header('Content-Disposition',
                               f'attachment; filename={name_file}')
                arquivo.close()
                msg.attach(att)
        else:
            arquivo = open(files, 'rb')
            att = MIMEBase('application', 'octet-stream')
            att.set_payload(arquivo.read())
            encoders.encode_base64(att)
            name_file = basename(files)
            print(name_file)
            att.add_header('Content-Disposition',
                           f'attachment; filename={name_file}')
            arquivo.close()
            msg.attach(att)
    try:
        connect_mail_send(para, msg)
        print(f'enviado com sucesso para {para}')
    except smtplib.SMTPException as e:
        print(f'ocorreu ao tentar enviar o email à {para} \nerro: {e}')
        raise e


def connect_mail_send(para, msg):
    with smtplib.SMTP(host=host, port=porta) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(user=my_mail, password=my_key)
        smtp.sendmail(my_mail, para, msg.as_string())

