
from fastapi import HTTPException

from services.connection import conectar, desconectar


def store_feedback(image_id: int, correct_classification: str):
    try:
        cnx, cur = conectar()
        cur.execute(
            "INSERT INTO tbl_feedbacks (image_id, correct_classification) VALUES (%s, %s);",
            (image_id, correct_classification))
        cnx.commit()
        
        # flag = True if 'positivo' in correct_classification else False
        # TODO - Inserir Feedback numa pasta ML

    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Erro ao armazenar feedback: {str(e)}")
    finally:
        desconectar(cnx, cur)
    return {"message": "Feedback armazenado com sucesso!"}


def get_feedback(image_id: int):
    try:
        cnx, cur = conectar()

        cur.execute(
            "SELECT image_id, correct_classification FROM tbl_feedbacks WHERE image_id = %s",
            (image_id, ))

        feedback = cur.fetchone()
        if feedback:
            return {
                "image_id": feedback[0],
                "correct_classification": feedback[1]
            }
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Erro ao obter feedback: {str(e)}")
    return None


def get_ocorrencias(id_user):
    try:
        cnx, cur = conectar()
        cur.execute("SELECT image_id FROM feedback")
        feedback_ids = cursor.fetchall()
        return [id[0] for id in feedback_ids]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter todos os IDs de feedback: {str(e)}")


def count_feedback_by_user(user_id):
    try:
        cnx, cur = conectar()
        cur.execute("SELECT COUNT(*) FROM tbl_feedbacks WHERE user_id = %s",
                    (user_id, ))
        result = cur.fetchone()
        return result[0] if result else 0
    except Exception as e:
        print(f"Error counting feedbacks: {str(e)}")
        return 0
    finally:
        desconectar(cnx, cur)
