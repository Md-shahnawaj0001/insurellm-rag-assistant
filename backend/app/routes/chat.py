from fastapi import APIRouter, Depends
from backend.app.models.chat_models import ChatRequest
from backend.app.services.rag_service import chat
from backend.app.dependencies.auth import get_current_user

router = APIRouter()


@router.post("/chat")
def chat_endpoint(
    request: ChatRequest,
    current_user=Depends(get_current_user)
):
    return chat(
        request.message,
        request.history,
        current_user.id,
        request.session_id
    )