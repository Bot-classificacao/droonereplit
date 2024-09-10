# Imports
import io
import random
import string
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Request, UploadFile, File, Form, APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from passlib.context import CryptContext
import mysql.connector

# # Configurações do banco de dados
# password = "S3nh@DBAVJG2024!!!$$$"
# encoded_password = urllib.parse.quote(password)

# SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://u611546537_DBA_VJ_GESTAO:{encoded_password}@srv720.hstgr.io/u611546537_VJ_GESTAO"
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# Configurações do MySQL
db_config_gambs = {
    'host': 'srv720.hstgr.io',
    'user': 'u611546537_DBA_VJ_GESTAO',
    'password': 'S3nh@DBAVJG2024!!!$$$',
    'db': 'u611546537_VJ_GESTAO'
}

# # Modelos de Banco de Dados
# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String(150), unique=True, nullable=False)
#     password_hash = Column(String(128), nullable=False)
#     temp_password = Column(Boolean, default=True)

#     def set_password(self, password):
#         self.password_hash = pwd_context.hash(password)

#     def check_password(self, password):
#         return pwd_context.verify(password, self.password_hash)

# class Empresa(Base):
#     __tablename__ = "empresas"

#     id = Column(Integer, primary_key=True, index=True)
#     cnpj = Column(String(20), unique=True, nullable=False)
#     nome = Column(String(100), nullable=False)
#     is_grupo = Column(Boolean, default=False)

# class Log(Base):
#     __tablename__ = "logs"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     action = Column(String(255), nullable=False)
#     timestamp = Column(DateTime, default=datetime.utcnow)
#     details = Column(String(1000), nullable=True)

#     user = relationship("User", backref="logs")

# Criação das tabelas
# Base.metadata.create_all(bind=engine)

# Inicializando o APIRouter
gambs = APIRouter()

# Contexto de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # Função para obter a sessão do banco de dados
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# Função para gerar senhas temporárias
def generate_temp_password():
    length = 12
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))


# Modelos Pydantic
class UserCreate(BaseModel):
    username: str


class UserUpdatePassword(BaseModel):
    new_password: str
    confirm_password: str


class EmpresaCreate(BaseModel):
    cnpj: str
    nome: str
    is_grupo: bool


# Rotas para manipulação de Usuários
# @gambs.post("/users/", response_model=dict)
# def create_user(user: UserCreate, db: Session = Depends(get_db)):
#     temp_password = generate_temp_password()
#     db_user = User(username=user.username)
#     db_user.set_password(temp_password)
#     db_user.temp_password = True

#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)

#     return {"username": db_user.username, "temp_password": temp_password}

# @gambs.put("/users/{user_id}/password", response_model=dict)
# def update_password(user_id: int,
#                     user_update: UserUpdatePassword,
#                     db: Session = Depends(get_db)):
#     db_user = db.query(User).filter(User.id == user_id).first()

#     if not db_user:
#         raise HTTPException(status_code=404, detail="Usuário não encontrado")

#     if user_update.new_password != user_update.confirm_password:
#         raise HTTPException(status_code=400, detail="Senhas não coincidem")

#     db_user.set_password(user_update.new_password)
#     db_user.temp_password = False
#     db.commit()
#     db.refresh(db_user)

#     return {"message": "Senha atualizada com sucesso"}

# # Rotas para manipulação de Empresas
# @gambs.post("/empresas/", response_model=dict)
# def add_empresa(empresa: EmpresaCreate, db: Session = Depends(get_db)):
#     db_empresa = Empresa(cnpj=empresa.cnpj,
#                          nome=empresa.nome,
#                          is_grupo=empresa.is_grupo)
#     db.add(db_empresa)
#     db.commit()
#     db.refresh(db_empresa)
#     return {"id": db_empresa.id, "message": "Empresa adicionada com sucesso"}

# @gambs.delete("/empresas/{empresa_id}", response_model=dict)
# def delete_empresa(empresa_id: int, db: Session = Depends(get_db)):
#     db_empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

#     if not db_empresa:
#         raise HTTPException(status_code=404, detail="Empresa não encontrada")

#     db.delete(db_empresa)
#     db.commit()
#     return {"message": "Empresa deletada com sucesso"}

# # Rotas para Logs
# @gambs.get("/logs/", response_model=dict)
# def get_logs(db: Session = Depends(get_db)):
#     logs = db.query(Log).order_by(Log.timestamp.desc()).all()
#     logs_list = [{
#         "user_id": log.user_id,
#         "action": log.action,
#         "timestamp": log.timestamp,
#         "details": log.details
#     } for log in logs]
#     return {"logs": logs_list}


# Rotas para o envio de formulários e manipulação de chaves
@gambs.post("/submit_form")
async def submit_form(emails: str = Form(...),
                      cnpjs: str = Form(...),
                      cnpj: str = Form(...),
                      proc_cert: str = Form(...),
                      cert_digital: UploadFile = File(...)):
    conn = mysql.connector.connect(**db_config_gambs)
    cursor = conn.cursor()

    # Lê o conteúdo do arquivo
    cert_digital_content = await cert_digital.read()

    cursor.execute(
        '''
        INSERT INTO forms (emails, cnpj, proc_cert, cert_digital, cnpjs, filename)
        VALUES (%s, %s, %s, %s, %s, %s)
        ''', (emails, cnpj, proc_cert, cert_digital_content, cnpjs,
              cert_digital.filename))
    conn.commit()

    return {"message": "Form data inserted successfully"}


@gambs.post("/verify_key")
async def verify_key(key: str):
    conn = mysql.connector.connect(**db_config_gambs)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM access_keys WHERE `key` = %s AND used = 0',
                   (key, ))
    valid_key = cursor.fetchone()
    if valid_key:
        cursor.execute('UPDATE access_keys SET used = 1 WHERE `key` = %s',
                       (key, ))
        conn.commit()
        return {"message": "Key is valid"}
    else:
        raise HTTPException(status_code=400, detail="Invalid or used key")


@gambs.post("/generate_key")
async def generate_key():
    new_key = str(uuid.uuid4())
    conn = mysql.connector.connect(**db_config_gambs)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO access_keys (`key`, used) VALUES (%s, %s)',
                   (new_key, 0))
    conn.commit()
    return {"message": "Key generated successfully"}


@gambs.get("/download_cert_digital/{form_id}")
async def download_cert_digital(form_id: int):
    conn = mysql.connector.connect(**db_config_gambs)
    cursor = conn.cursor()
    cursor.execute('SELECT cert_digital, filename FROM forms WHERE id = %s',
                   (form_id, ))
    result = cursor.fetchone()
    if result:
        cert_digital_blob, filename = result
        return StreamingResponse(io.BytesIO(cert_digital_blob),
                                 media_type="application/octet-stream",
                                 headers={
                                     "Content-Disposition":
                                     f"attachment; filename={filename}"
                                 })
    else:
        raise HTTPException(status_code=404, detail="Certificate not found")


@gambs.get("/forms")
async def get_forms():
    conn = mysql.connector.connect(**db_config_gambs)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'SELECT id, emails, cnpjs, cnpj, proc_cert, filename FROM forms')
    forms = cursor.fetchall()
    return forms


@gambs.get("/view_keys")
async def view_keys():
    conn = mysql.connector.connect(**db_config_gambs)
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, `key`, used FROM access_keys')
    keys = cursor.fetchall()
    return keys
