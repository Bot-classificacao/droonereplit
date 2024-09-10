import requests

import requests

url_send = 'https://efea37cf-0d56-4e3d-9823-0d7598a15284-00-17uxzbltcwyyz.spock.replit.dev:8000/whats/send'  # URL da API
url_get = 'https://efea37cf-0d56-4e3d-9823-0d7598a15284-00-17uxzbltcwyyz.spock.replit.dev:8000/whats'  # URL da API


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
