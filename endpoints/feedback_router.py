from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys, os
from pathlib import Path

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

sys.path.insert(0, os.curdir)
from services.feedback.feedback import store_feedback, get_feedback, count_feedback_by_user
from services.feedback.cams_db import getImages, getImagesCount, remove_image_blob
from services.connection import conectar, desconectar

router = APIRouter()



class FeedbackRequest(BaseModel):
    image_id: int
    correct_classification: str


@router.post("/post")
async def feedback_router(request: FeedbackRequest):
    try:
        response = store_feedback(
            image_id=request.image_id,
            correct_classification=request.correct_classification)

        # Após o feedback, remove o blob da imagem
        remove_image_blob(request.image_id)

        return response
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get/{image_id}")
async def get_feedback_router(image_id: int):
    try:
        feedback_data = get_feedback(image_id)
        if feedback_data:
            return feedback_data
        else:
            raise HTTPException(status_code=204, detail="Feedback not found")
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class OccurrencesResponse(BaseModel):
    id_user: int
    tipo: int


@router.post("/get_occurrences")
async def get_occurrences(request: OccurrencesResponse):
    try:
        if request.tipo == 1:
            print("== Contando as ocorrências ==")
            count = getImagesCount(request.id_user)
            #feedback_count = count_feedback_by_user(request.id_user)
            #, "feedback_count": feedback_count
            return {"count": count}

        elif request.tipo == 2:
            print("== Selecionando todas as ocorrências ==")
            images = getImages(request.id_user)
            if images:
                return {"images": images}
            else:
                raise HTTPException(status_code=204, detail="No images found.")
        else:
            raise HTTPException(status_code=400,
                                detail="Invalid type specified.")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-alerts/{user_id}")
async def get_alerts(user_id: int):
    cnx, cur = conectar()
    try:
        query = """
        SELECT I.* FROM tbl_imagens I
        WHERE id_user = %s AND alert_status = 'new'
        """
        cur.execute(query, (user_id, ))
        alerts = cur.fetchall()

        # Marcar os alertas como mostrados
        update_query = """
        UPDATE tbl_imagens SET alert_status = 'shown'
        WHERE id_user = %s AND alert_status = 'new'
         """
        cur.execute(update_query, (user_id, ))
        cnx.commit()

        return {"alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Error retrieving alerts: {str(e)}")
    finally:
        desconectar(cnx, cur)
