from classconection import ClassConnection

config = {
    'host': 'srv720.hstgr.io',
    'user': 'u611546537_DBA_Droone',
    'password': 'S3nh@FOrt3DBA_DrOOne_2024###',
    'database': 'u611546537_Droone'
}

clsconn = ClassConnection(**config)

try:
  conn = clsconn.connected()
  if conn is not None:
    cur = clsconn.get_cursor()

    @clsconn.query
    def select_all():
      query = 'select * from tbl_users'
      cur.execute(query)
      selecao = cur.fetchall()
      return selecao

    # Consumir os resultados sem precisar usá-los
    print(select_all())

finally:
  pass
