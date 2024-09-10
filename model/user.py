from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field, validator


# Contexto do Passlib para hash de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Modelos Pydantic
class User_create(BaseModel):
    username: str = Field(...,
                          min_length=3,
                          max_length=20,
                          pattern=r"^[a-zA-Z0-9_]*$")
    email: EmailStr
    password: str

    @validator('username')
    def check_username(cls, value):
        # REGEX Removido
        return value

    @validator('password')
    def check_password(cls, value):
        # REGEX removido
        return value



class User_login(BaseModel):
    email: EmailStr
    password: str

    @validator('password')
    def check_password(cls, value):
        # REGEX removido
        return value


# Funções auxiliares para hash e verificação de senha
def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

