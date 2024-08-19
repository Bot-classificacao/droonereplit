async def get_mail() -> dict:
  print("Iniciando get_mail")
  try:
      with MailBox('imap.hostinger.com',
                   993).login(username=mail_name_listener,
                              password=mail_pass_listener,
                              initial_folder='INBOX') as mailbox:
          print("Conexão estabelecida com sucesso")
          msgs = mailbox.fetch(AND(subject='ALERTA DVR'),
                               sort='DATE',
                               reverse=True)
          # print(f"Número de e-mails encontrados: {len(list(msgs))}")
          # sorted_emails = sorted(msgs, key=lambda msg: msg.date, reverse=True)
          if msgs:
              for msg in msgs:
                  sender = msg.from_
                  subject = msg.subject
                  body = msg.text
                  date_mail = msg.date.strftime('%Y-%m-%d %H:%M:%S')
                  filenames = get_imagem(msg.attachments)
                  # if len(msg.attachments) > 0:
                  #     for anexo in msg.attachments:
                  #         name_att = anexo.filename
                  #         filename.append(name_att)
                  #         # tranforma em bytes a img
                  #         bytes_img = anexo.payload
                  #         dir_img = f'classificador\\classificadorIA\\queue\\{name_att}'
                  #         with open(dir_img, 'wb') as anx:
                  #             anx.write(bytes_img)
                  #         #     img_path = await get_imagem(anexo)
                  #         # if img_path:
                  #         #     filename.append(img_path)
                  # if filename:
                  print("Retornando e-mail processado")
                  print("subject: ", subject)
                  return {
                      'sender': sender,
                      'subject': subject,
                      'body': body,
                      'date': date_mail,
                      'filename': filenames,
                  }
          print("Nenhum e-mail com o assunto especificado encontrado")
  except Exception as e:
      print(f"Erro ao acessar o servidor de e-mail: {e}")
  return None

