from model.classconection import ClassConnection
import os

config = {
    'host': 'srv720.hstgr.io',
    'user': 'u611546537_DBA_Droone',
    'password': 'S3nh@FOrt3DBA_DrOOne_2024###',
    'database': 'u611546537_Droone'
}
cls = ClassConnection(**config)
conn = cls.connected()
cursor = cls.get_cursor()


def apply_images(email):
  filenames = email['filename']
  status_img = 'a processar'
  if filenames is None or len(filenames) < 1:
    filenames = []
    return {'path': '', 'status': status_img}
  else:
    dir_atual = os.getcwd()
    path_files_str = ''
    for file in filenames:
      if '.png' in file or '.jpeg' in file or '.jpg' in file:
        path_files_str+= ' ' + \
            os.path.join(dir_atual, file)
      else:
        continue
    status_img = 'processada'
    return {'path': path_files_str, 'status': status_img}


@cls.query
def get_image_id_by_date(date):
  query = f"select i.id_imagem from tbl_imagens i where datetime_chegada = '{date}'"
  cursor.execute(query)
  result = cursor.fetchone()
  return result


@cls.update
def update_image_by_id(id):
  query = f"update tbl_imagens set status = 'processada' where id_imagem = {id}"
  cursor.execute(query)


def fill_list_images(email):
  pass
