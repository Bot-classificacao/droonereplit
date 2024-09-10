from fastapi import FastAPI, APIRouter

router = APIRouter()

dados = {'Numero': '', 'msg': '', 'Periodo': ''}


@router.post('/whats/send')
def envio(numero: str, msg: str, temp: str):
    print('enviando mensagem para API')
    dados['Numero'] = numero
    dados['msg'] = msg
    dados['Periodo'] = temp
    return dados


@router.get('/whats')
def home():
    return dados
