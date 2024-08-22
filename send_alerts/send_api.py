import datetime
from fastapi import FastAPI
import uvicorn
'''uvicorn send_api:app --reload --host 0.0.0.0 --port 8000'''
app = FastAPI()

dados = {'Numero': '', 'msg': '', 'Periodo': ''}


@app.post('/send')
def envio(numero: str, msg: str, periodo: str):
  dados['Numero'] = numero
  dados['msg'] = msg
  dados['Periodo'] = periodo


@app.get('/whats')
def home():
  return dados

if __name__ == "__main__":
  print('Subindo API do whatsapp..')
  uvicorn.run(app=app, host="0.0.0.0", port=8000)
