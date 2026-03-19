from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.domain.services.ask_service import ask_question

router = APIRouter()


class AskRequest(BaseModel):
    question: str


@router.post("/ask")
def ask(request: AskRequest):
    """POST /ask — Input: { "question": "..." }
    Output: { cypher, data, graph, answer }
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = ask_question(request.question)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process question: {str(e)}"
        )
