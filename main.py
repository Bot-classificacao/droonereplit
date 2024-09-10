import asyncio
import sqlite3
from contextlib import asynccontextmanager
from threading import Thread

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse

import services.connection as conn

# Importar os roteadores
from endpoints.auth_router import router as auth_router
from endpoints.classificador_router import router as classificador_router
from endpoints.feedback_router import router as feedback_router
from endpoints.gambiarra_simulator import gambs as gambs_router
from endpoints.robotdog_router import router as robotdog_router
from endpoints.whats_router import router as whats_router
from services.feedback.blob import router as blob_router
from services.feedback.recept_mail import classify_email

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


@app.get("/")
async def homepage():
    return FileResponse("static/index.html")


# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(classificador_router,
                   prefix="/classificador",
                   tags=["classificador"])
app.include_router(robotdog_router, prefix="/robotdog", tags=["robotdog"])
app.include_router(feedback_router, prefix="/feedback", tags=["feedback"])
app.include_router(blob_router, prefix="/blob", tags=["blob"])
app.include_router(whats_router, tags=["whats"])

app.include_router(gambs_router, prefix="/gambs", tags=["gambiarra"])


# Thread listener email
def listener_email():
    print("Listener rodando...")
    global listener
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(classify_email())


if __name__ == "__main__":
    print('iniciando thred listener...')
    email_thread = Thread(target=listener_email)
    email_thread.start()
    print('Subindo a API main...')
    uvicorn.run(app, port=8000, reload=False)
