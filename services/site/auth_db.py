from fastapi import HTTPException
from passlib.context import CryptContext

from ..connection import conectar, desconectar, get_connection

import string
import random

# Contexto do Passlib para hash de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Funções auxiliares para hash e verificação de senha
def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Register function
async def register(user):
    hashed_password = get_password_hash(user.password)
    try:
        print("== Usuário sendo registrado")
        cnx, cur = conectar()
        print("==+ Usuário sendo registrado")

        # Verificar se o usuário já existe
        cur.execute('SELECT * FROM tbl_usermails WHERE email = %s',
                    (user.email, ))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Email já existe")

        cur.execute('SELECT * FROM tbl_users WHERE nome = %s',
                    (user.username, ))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Username já existe")

        # Inserir email
        print("==== Cadastrando email no banco de dados")
        cur.execute('INSERT INTO tbl_usermails (email) VALUES (%s)',
                    (user.email, ))
        cnx.commit()

        # Selecionar o ID do email recém inserido
        print("=== Selecionando id do banco")
        cur.execute('SELECT id_email FROM tbl_usermails WHERE email = %s',
                    (user.email, ))
        id_email = cur.fetchone()

        if not id_email:
            raise HTTPException(status_code=400,
                                detail="Email não autenticado no sistema")

        print(f"=== ID do email: {id_email[0]}")
        id_email = int(id_email[0])

        # Inserir usuário
        print("==== Cadastrando usuário")
        cur.execute(
            'INSERT INTO tbl_users (nome, senha, fk_email) VALUES (%s, %s, %s)',
            (user.username, hashed_password, id_email))
        cnx.commit()

        print("=== Verificando se usuário foi inserido")
        cur.execute(
            """
            SELECT * FROM tbl_users WHERE fk_email = %s
        """, (id_email, ))
        db_user = cur.fetchone()
        print("=== Usuário inserido com sucesso")
        desconectar(cnx, cur)

        if db_user:
            return {"message": "Usuário registrado com sucesso!"}
        else:
            return HTTPException(
                status_code=500,
                detail="Falha ao registrar usuário no banco de dados.")

    except Exception as e:
        print(f"Erro ao registrar o usuário: {e}")
        raise HTTPException(status_code=500,
                            detail=f"Falha ao registrar usuário: {str(e)}")


# Login Function
async def login(user):
    try:
        cnx, cur = conectar()
        cur.execute('SELECT id_email FROM tbl_usermails WHERE email = %s',
                    (user.email, ))

        id_email = cur.fetchone()

        if not id_email:
            return HTTPException(status_code=400,
                                 detail="E-Mail não encontrado.")

        cur.execute('SELECT * FROM tbl_users WHERE fk_email = %s',
                    (id_email[0], ))
        db_user = cur.fetchone()

        desconectar(cnx, cur)
        if db_user:
            print("=== Usuário encontrado")
            if verify_password(user.password, db_user[2]):
                return {
                    "message": "Login com sucesso!",
                    "id_cliente": db_user[0],
                    "name": db_user[1],
                    "email": user.email
                }
            else:
                return HTTPException(status_code=400,
                                     detail="Credenciais Inválidas. . .")
        else:
            print("=== Usuário não encontrado")
            return HTTPException(status_code=400,
                                 detail="Usuário não encontrado.")
    except Exception as e:
        return HTTPException(status_code=500, detail=f"Erro: {str(e)}")


#  Generate Token Function
async def generate_token(user):

    try:
        print("# Gerando token")
        cnx, cur = conectar()
        query = "SELECT id_email FROM tbl_usermails WHERE email = %s"
        cur.execute(query, (user.email, ))
        id_email = cur.fetchone()
        print("# SELECT ID EMAIL CONCLUIDO")
        if id_email:
            token = ''.join(
                random.choice(string.ascii_uppercase + string.digits)
                for _ in range(5))
            cur.execute(
                'INSERT INTO tbl_tokens (email, token) VALUES (%s, %s, 0)',
                (user.email, token))
            print("# Token salvo no BD")
            cnx.commit()
            desconectar(cnx, cur)
            return token

    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Erro ao gerar token: {str(e)}") from e


#  Validate Token Function
async def validate_token(user):

    try:
        cnx, cur = conectar()

        print("=== VALIDATE TOKEN")
        cur.execute('SELECT fk_email FROM tbl_users INNER JOIN tbl_usermails ON tbl_user.fk_email = tbl_usermails.id_email WHERE tbl_usermails.email = %s LIMIT 1',         (user.email, ))
        id_email = cur.fetchone()
        print(f"==== ID EMAIL: {id_email}")
        if id_email:
            cur.execute(
                'SELECT * FROM tbl_tokens WHERE email = %s AND token = %s AND usado = 0 LIMIT 1;',
                (user.email, user.token))

            is_valid = cur.fetchone()
            print(f"==== IS VALID: {is_valid[0]}")

            if is_valid:
                cur.execute('UPDATE tbl_tokens SET usado = 1 WHERE email = %s',
                            (user.email, ))

                cnx.commit()

                return {'message': 'Sucesso. Token Válido!'}
        desconectar(cnx, cur)
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Erro ao validar o token: {str(e)}") from e


#  Validate Token Function
async def forgot_pass(user):
    hashed_password = get_password_hash(user.senha)

    try:
        cnx, cur = conectar()

        cur.execute('SELECT * FROM tbl_users WHERE email = %s', (user.email, ))

        if not cur.fetchone():
            raise HTTPException(status_code=400, detail="Email não existe.")

        cur.execute('UPDATE tbl_users SET password = %s WHERE email = %s', (
            hashed_password,
            user.email,
        ))
        cnx.commit()

        cur.execute('SELECT * FROM tbl_users WHERE email = %s', (user.email, ))
        db_user = cur.fetchone()
        cur.close()
        desconectar(cnx, cur)
        if db_user:
            return {"message": "Senha atualizada!"}
        else:
            raise HTTPException(
                status_code=500,
                detail=
                "Falha ao atualizar a senha do usuário no banco de dados.")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar a senha: {str(e)}") from e
