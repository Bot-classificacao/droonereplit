from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from services.feedback.feedback import store_feedback, get_feedback, get_all_feedback_ids

router = APIRouter()


# BaseModel para o feedback
class FeedbackRequest(BaseModel):
    image_id: int
    correct_classification: str


# Endpoint para enviar feedback
@router.post("/post")
async def feedback_router(request: FeedbackRequest):
    try:
        response = store_feedback(
            image_id=request.image_id,
            correct_classification=request.correct_classification)
        return response
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint para obter feedback
@router.get("/get/{image_id}")
async def get_feedback_router(image_id: int):
    try:
        feedback_data = get_feedback(image_id)
        if feedback_data:
            return feedback_data
        else:
            raise HTTPException(status_code=404, detail="Feedback not found")
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint para obter todos os IDs de feedback pendentes
@router.get("/get_all_ids", response_model=List[int])
async def get_all_feedback_ids_router():
    try:
        feedback_ids = get_all_feedback_ids()
        return feedback_ids
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
