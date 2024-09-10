import requests

import requests

url_send = 'https://ba2add21-2f50-4d9e-84c9-1c06ee3cb5e3-00-1bm00jl761pt7.worf.replit.dev:8000/whats/send'  # URL da API
url_get = 'https://ba2add21-2f50-4d9e-84c9-1c06ee3cb5e3-00-1bm00jl761pt7.worf.replit.dev:8000/whats'  # URL da API


def postar(numero: str, mensagem: str, periodo: str):
  # Dados que serão enviados no POST
  dados = {'numero': numero, 'msg': mensagem, 'temp': periodo}

  # Fazendo a requisição POST com os dados no formato JSON
  response_post = requests.post(url_send, params=dados)
  response_get = requests.get(url_get)
  print(response_get)

  # Exibindo a resposta da API
  #print("Resposta da API:", response2.json())


#postar('1998722472', 'Teste API', '20/02/2005')
