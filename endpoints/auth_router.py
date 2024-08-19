from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

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
    user = User_create(username=request.username, email=request.email, password=request.password)
    return await auth.register(user)

# BaseModel de Login
class LoginRequest(BaseModel):
    email: str
    password: str

# Endpoint de login
@router.post("/login")
async def login_router(request: LoginRequest):
    user = User_login(email=EmailStr(request.email), password=request.password)
    return await auth.login(user)

# Endpoint de teste
@router.post("/teste")
async def teste() -> str:
    return 'teste'
