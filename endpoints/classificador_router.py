from fastapi import APIRouter, File, HTTPException, UploadFile
from services.classificador.classifier_alert_report import (
    carregar_ou_treinar_modelo,  
    classificar_imagem_com_ia
)
import shutil

router = APIRouter()

@router.post("/classificar-imagem/")
async def classificar_imagem(file: UploadFile = File(...)):
    try:
        modelo = carregar_ou_treinar_modelo()
        caminho_imagem = f"classificador/classificadorIA/queue/{file.filename}"
        with open(caminho_imagem, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        classe, confianca = classificar_imagem_com_ia(caminho_imagem, modelo)  
        return {"classe": classe, "confiança": confianca}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.get("/train-model/")
async def treinar():
    try:
        modelo = carregar_ou_treinar_modelo()
        return {"status": "Modelo treinado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e