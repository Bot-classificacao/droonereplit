import asyncio
import sqlite3
import subprocess
from contextlib import asynccontextmanager
from typing import Dict, List
import sys

from starlette.responses import FileResponse, JSONResponse
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from threading import Thread

import services.connection as conn

# Importar os roteadores
from endpoints.auth_router import router as auth_router
from endpoints.classificador_router import router as classificador_router
from endpoints.feedback_router import router as feedback_router
from endpoints.robotdog_router import router as robotdog_router
from services.feedback.recept_mail import classify_email
from model.user import get_user_by_email

sys.path.append('/home/runner/drooneapi')

app = FastAPI()


# Event handlers using lifespan
@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        conn.setup_database()
        print("Database setup completed successfully.")
    except Exception as e:
        print(f"Erro ao iniciar o banco de dados: {e}")
    yield
    print("Cleanup actions can be performed here")


app.router.lifespan_context = lifespan

# Configurar CORS para lidar com requisições de várias origens
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas as origens
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT",
                   "DELETE"],  # Permitir métodos
    allow_headers=["*"],  # Permitir todos os cabeçalhos
)


# Adicionando rota OPTIONS para /auth/register
@app.options("/auth/register")
async def options_register():
    return JSONResponse(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
        status_code=204  # Sem conteúdo
    )


@app.get("/")
async def homepage():
    return FileResponse("static/index.html")


# LISTENER TEST
global listener
listener = 0


@app.get("/sinal")
def ver_sinal():
    global listener
    return {"listener": listener}


def sinal_divino(alistener):
    alistener += 1
    return alistener


@app.get("/get-users")
def get_users_page():
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()
    users = [{"id": row[0], "name": row[1], "email": row[2]} for row in rows]
    return users


@app.get("/user/{email}")
async def get_user(email: str):
    try:
        user = await get_user_by_email(email)
        if user:
            return user
        else:
            raise HTTPException(status_code=404,
                                detail="Usuário não encontrado")
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Erro ao buscar usuário: {str(e)}")


# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(classificador_router,
                   prefix="/classificador",
                   tags=["classificador"])
app.include_router(robotdog_router, prefix="/robotdog", tags=["robotdog"])
app.include_router(feedback_router, prefix="/feedback", tags=["feedback"])


# Thread listener email
def listener_email():
    print("Listener rodando...")
    global listener
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(classify_email())
    listener = sinal_divino(listener)

def run_api_whats():
    filepath = 'send_alerts/send_api.py'
    subprocess.run(['python', filepath])
    
if __name__ == "__main__":
    email_thread = Thread(target=listener_email)
    email_thread.start()
    whats_thread = Thread(target=run_api_whats)
    whats_thread.start()

    uvicorn.run(app, host="0.0.0.0", port=8080)
