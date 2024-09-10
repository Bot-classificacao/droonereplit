import sqlite3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from send_alerts.sender_mail import message_send

from model.user import User_create, User_login
from services.site import auth_db as auth

router = APIRouter()


# BaseModel de Registro
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


# Endpoint de registro
@router.post("/register")
async def register_router(request: RegisterRequest):
    user = User_create(username=request.username,
                       email=request.email,
                       password=request.password)
    return await auth.register(user)


# BaseModel de Login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Endpoint de login
@router.post("/login")
async def login_router(request: LoginRequest):
    # Descriptografar o email e senha
    user = User_login(email=EmailStr(request.email), password=request.password)
    return await auth.login(user)

# BaseModel de TokenRequest
class TokenRequest(BaseModel):
    email: EmailStr


# BaseModel de Validação do Token
class TokenValidateRequest(BaseModel):
    email: EmailStr
    token: str


# BaseModel de Validação do Token
class ChangePasswordForgot(BaseModel):
    email: EmailStr
    token: str
    senha: str


# Endpoint de Geração de Token
@router.post("/generate_token")
async def generate_token_end(request: TokenRequest):
    user = TokenRequest(email=EmailStr(request.email))

    # GERA UM TOKEN DE 6 DÍGITOS E ARMAZENA NUMA TABELA DO SQLITE
    token = await auth.generate_token(user)

    if token:
        # Enviando o e-mail com o token
        message_send(str(user.email),
                     '[DROONE] Solicitação de alteração de senha',
                     f'O seu token de alteração de senha é: {token}')

        return {"message": "Token gerado com sucesso!"}
    return {'message': 'Erro na geração do token.'}


# Endpoint de validação de Token
@router.post("/validate_token")
async def validate_token_end(request: TokenValidateRequest):
    user = TokenValidateRequest(email=EmailStr(request.email),
                                token=request.token)

    if await auth.validate_token(user):
        return {"message": "Token validado!"}

    return {'message': 'Token inválido.'}

# Endpoint de troca de Senha (esqueceu)
@router.post("/forgot_pass")
async def forgot_pass_end(request: ChangePasswordForgot):
    user = ChangePasswordForgot(email=EmailStr(request.email),
                                token=request.token,
                                senha=request.senha)

    return await auth.forgot_pass(user)

# get all users
@router.get("/get-users")
def get_users_page():
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tbl_users")
    rows = cursor.fetchall()
    conn.close()
    users = [{"id": row[0], "name": row[1], "email": row[2]} for row in rows]
    return users

# Get user by email
@router.get("/user/{email}")
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
                            detail=f"Erro ao buscar usuário: {str(e)}") from e




# Endpoint de teste
@router.post("/teste")
async def teste() -> str:
    return 'teste'
