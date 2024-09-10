  '''

  import sqlite3
  import mysql.connector

  from services.connection import conectar

  # Conectar ao banco de dados SQLite
  conn_sqlite = sqlite3.connect('test.db')
  cursor_sqlite = conn_sqlite.cursor()

  # Executar SELECT na tabela Users do SQLite
  cursor_sqlite.execute("SELECT * FROM Users")
  users = cursor_sqlite.fetchall()

  # Obter informações sobre as colunas
  cursor_sqlite.execute("PRAGMA table_info(Users)")
  columns = [column[1] for column in cursor_sqlite.fetchall()]

  # Fechar conexão com SQLite
  conn_sqlite.close()

  # Conectar ao banco de dados MySQL
  conn_mysql = mysql.connector.connect(
      host='srv720.hstgr.io',
      user='u611546537_DBA_Droone',
      password='S3nh@FOrt3DBA_DrOOne_2024###',
      database='u611546537_Droone'
  )
  cursor_mysql = conn_mysql.cursor()


  # Criar a tabela Users no MySQL (se não existir)
  create_table_query = f"CREATE TABLE IF NOT EXISTS Users ({', '.join([f'{col} TEXT' for col in columns])})"
  cursor_mysql.execute(create_table_query)

  # Inserir dados na tabela Users do MySQL
  insert_query = f"INSERT INTO Users ({', '.join(columns)}) VALUES ({', '.join(['%s' for _ in columns])})"
  cursor_mysql.executemany(insert_query, users)

  # Commit das alterações e fechar conexão com MySQL
  conn_mysql.commit()
  conn_mysql.close()

  print("Transferência de dados concluída com sucesso!")

  '''

  import io
  import os
  import sys

  from PIL import Image

  sys.path.append(os.getcwd())
  from services.connection import conectar, desconectar

  IMAGES_PATH = 'classificador/classificadorIA/classificados/Não Autorizado'
  QUEUE_PATH = 'classificador/classificadorIA/queue'

  DB_HOST, DB_USER, DB_PASSWORD, DB_NAME = '', '', '', ''

  def get_images_from_directory(path):
      print("Get images")
      images = []
      for filename in os.listdir(path):
          if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
              images.append((filename, os.path.join(path, filename)))
      return images

  def get_images_from_bd():
      print("=== Getting Images from BD")
      try:
          cnx, cur = conectar(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
          query = "SELECT * FROM tbl_imagens"
          cur.execute(query)
          images = cur.fetchall()
          desconectar(cnx, cur)
          return images
      except Exception as e:
          print(f"Erro tentando coletar as imagens: {str(e)}")
          return []


  def image_to_byte_array(image_path):
      with Image.open(image_path) as img:
          byte_arr = io.BytesIO()
          ext = os.path.splitext(image_path)[1].lower()
          format = 'JPEG' if ext in ['.jpeg', '.jpg'] else 'PNG'
          img.save(byte_arr, format=format)
          print("Imagem convertida para byte array.")
          return byte_arr.getvalue()

  def save_image_blob(filename, image_path):
      try:
          print("==== Image Path: ", image_path)
          with open(image_path, 'rb') as file:
              blob = file.read()

          print("==== Blob:", blob)
          cnx, cur = conectar(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
          query = "UPDATE tbl_imagens SET blob_imagens = %s WHERE path LIKE %s"
          cur.execute(query, (blob, f"%{filename}%"))
          cnx.commit()
          print("Blob updated for: ", image_path)
      except Exception as e:
          print(f"Error saving blob: {str(e)}")
      finally:
          desconectar(cnx, cur)

  def update_image_path(filename, new_path):
      try:
          query = "UPDATE tbl_imagens SET path = %s WHERE path LIKE %%s%%"
          cnx, cur = conectar(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
          cur.execute(query, (new_path, f"%{filename}%"))
          cnx.commit()
      except Exception as e:
          print(f"Error updating image path: {str(e)}")
      finally:
          desconectar(cnx, cur)




  images = get_images_from_directory(IMAGES_PATH)
  imagesbd = get_images_from_bd()

  for imgbd in imagesbd:
      if "Não Autorizado" in imgbd[3]:
          print(f"=== Imagem: {imgbd[3]}\n")

          for name, path in images:
              if name in imgbd[3]:
                  print("===== Imagem encontrada no diretório: ", name)
                  update_image_path(name, path)
                  save_image_blob(name, path)


  #    print(f"=== Imagem: {img}")
