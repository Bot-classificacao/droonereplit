from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.alerts import enviar_alerta_whatsapp, enviar_alerta_email

router = APIRouter()

class AlertaRequest(BaseModel):
    telefone: str
    mensagem: str

@router.post("/send-alert-whatsapp/")
async def send_alert_whatsapp(request: AlertaRequest):
    try:
        enviar_alerta_whatsapp(request.telefone, request.mensagem)
        return {"status": "Alerta enviado via WhatsApp com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-alert-email/")
async def send_alert_email(email: str):
    try:
        enviar_alerta_email(email)
        return {"status": "Alerta enviado via Email com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
