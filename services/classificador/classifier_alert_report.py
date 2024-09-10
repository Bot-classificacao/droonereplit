import os
import shutil
import numpy as np
import tensorflow as tf

from send_alerts.send_with_api import postar
from services.alerts import enviar_alerta_whatsapp, enviar_alerta_email

from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from sklearn.model_selection import train_test_split

from services.feedback.blob import save_image_blob, update_image_path
from services.utils import image_save, image_to_byte_array, image_update

# Diretórios de dados
train_data_dir = "classificador/classificadorIA/Treinamento"
validation_data_dir = "classificador/classificadorIA/Validation"
classes = [
    d for d in os.listdir(train_data_dir)
    if os.path.isdir(os.path.join(train_data_dir, d))
] + [
    d for d in os.listdir(validation_data_dir)
    if os.path.isdir(os.path.join(validation_data_dir, d))
]

# Caminho do modelo
model_path = "classificador/classificadorIA/model_classificacao_faces.h5"


def carregar_imagens(diretorio_base, classes):
    imagens = []
    etiquetas = []
    for classe in classes:
        diretorio_classe = os.path.join(diretorio_base, classe)
        if os.path.isdir(diretorio_classe):
            for nome_arquivo in os.listdir(diretorio_classe):
                caminho_arquivo = os.path.join(diretorio_classe, nome_arquivo)
                if os.path.isfile(caminho_arquivo):
                    try:
                        imagem = load_img(caminho_arquivo,
                                          target_size=(224, 224))
                        imagem = img_to_array(imagem)
                        imagem /= 255.0
                        imagens.append(imagem)
                        etiquetas.append(classes.index(classe))
                    except Exception as e:
                        print(
                            f"Erro ao carregar imagem {caminho_arquivo}: {e}")
    return np.array(imagens), np.array(etiquetas)


def carregar_ou_treinar_modelo():
    if os.path.exists(model_path):
        try:
            print("Carregando modelo existente...")
            return load_model(model_path)
        except Exception as e:
            print(f"Erro ao carregar modelo: {e}, treinando novo modelo...")
            return treinar_modelo()
    else:
        print("Modelo não encontrado. Treinando novo modelo...")
        return treinar_modelo()


def treinar_modelo():
    print("Iniciando o treinamento do modelo...")
    modelo = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(len(classes), activation='softmax')
    ])
    modelo.compile(optimizer='adam',
                   loss='sparse_categorical_crossentropy',
                   metrics=['accuracy'])
    imagens_treino, etiquetas_treino = carregar_imagens(
        train_data_dir, classes)
    imagens_val, etiquetas_val = carregar_imagens(validation_data_dir, classes)
    if len(imagens_treino) > 0 and len(imagens_val) > 0:
        modelo.fit(imagens_treino,
                   etiquetas_treino,
                   epochs=10,
                   validation_data=(imagens_val, etiquetas_val))
        modelo.save(model_path)
        print("Modelo treinado e salvo com sucesso.")
    else:
        print("Falha ao carregar imagens para treinamento.")
    return modelo


def classificar_imagem_com_ia(caminho_imagem,
                              modelo,
                              email=None,
                              whats_cliente=None,
                              periodo=None):
    print(f"Classificando imagem: {caminho_imagem}")
    if 'Não há anexo' in caminho_imagem:
        print('Não há anexo, logo não será processada')
        return None, None
    imagem = load_img(caminho_imagem, target_size=(180, 180))
    imagem = img_to_array(imagem)
    imagem = np.expand_dims(imagem, axis=0)
    imagem = imagem / 255.0
    try:
        predicao = modelo.predict(imagem)
        indice = np.argmax(predicao[0])
        classe = classes[indice]
        confianca = predicao[0][indice] * 100

        destino = os.path.join(
            "classificador/classificadorIA/classificados",
            "Autorizado" if classe == "Autorizado" else "Não Autorizado",
            caminho_imagem.split('/')[-1])

        try:
            shutil.move(caminho_imagem, destino)
        except Exception as e:
            print(e)

        print(f"Imagem classificada como {classe} com confiança {confianca}%")

        if confianca < 70 and classe == "Não Autorizado":
            ass = f""" <p>Alerta de Acesso Não Autorizado",</p>
                        <p>Acesso não autorizado detectado com {confianca:.2f}% de confiança.</p>
                        <p>caminho da imagem:{[destino]}</p>
            """

            whats_msg = f"""
            Alerta de segurança: Acesso não autorizado detectado com {confianca:.2f}% de confiança.
            """
            if email != None:
                # def message_send(para, assunto, mensagem, files=None):
                enviar_alerta_email(email, 'Alerta - Droone', ass,
                                    caminho_imagem)
            if whats_cliente != None:
                postar(whats_cliente, whats_msg, periodo)
                print('API sensibilizada')
                # enviar_alerta_whatsapp(whats_cliente, whats_msg)

        return classe, confianca
    except Exception as e:
        print(f"Erro durante a predição: {e}")
        return None, None


def processar_nova_imagem(caminho_imagem, modelo, email, whats_cliente,
                          periodo):
    print('processando nova imagem')
    classe, confianca = classificar_imagem_com_ia(caminho_imagem, modelo,
                                                  email, whats_cliente,
                                                  periodo)
    destino_base = "classificador/classificadorIA/classificados"
    destino = os.path.join(
        destino_base,
        "Autorizado" if classe == "Autorizado" else "Não Autorizado")

    # Verifica e cria o diretório se não existir
    os.makedirs(destino, exist_ok=True)

    destino_final = os.path.join(destino, os.path.basename(caminho_imagem))
    try:
        shutil.move(caminho_imagem, destino_final)
    except Exception as e:
        print(e)
        pass
    else:
        print(
            f"Imagem {os.path.basename(caminho_imagem)} movida para {destino}")

    if classe == "Não Autorizado":
        # Transforma imagem em blob
        #blob = image_to_byte_array(destino_base+caminho_imagem)
        nome_arquivo = os.path.basename(caminho_imagem)
        # Conferindo se o destino final inclui o proprio nome do arquivo
        # Se não incluir: destino_final + nome_arquivo
        print(destino_final)
        # Caminho antigo, caminho novo
        # Nome do arquivo, caminho novo (Nao autorizado)
        update_image_path(nome_arquivo, destino_final)
        save_image_blob(destino_final)
        print(
            f"Imagem {os.path.basename(caminho_imagem)} atualizada com sucesso."
        )


# Carregar ou treinar o modelo
modelo = carregar_ou_treinar_modelo()

# Caminho para uma imagem de teste
# TODO - TESTE
#caminho_imagem_teste = "classificador/classificadorIA/queue/cet-640x409.jpg"
#processar_nova_imagem(caminho_imagem_teste, modelo)
