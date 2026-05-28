from fastapi import APIRouter, Depends
from backend.app.db.database import SessionLocal
from backend.app.db.models import ChatSession, Message
from backend.app.models.chat_models import RenameChatRequest
from backend.app.dependencies.auth import get_current_user

router = APIRouter()


@router.get("/history")
def get_all_history(current_user=Depends(get_current_user)):
    db = SessionLocal()

    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).all()

    result = []

    for session in sessions:
        result.append({
            "id": session.id,
            "title": session.title,
            "created_at": session.created_at
        })

    db.close()
    return result


@router.get("/history/{session_id}")
def get_single_history(
    session_id: int,
    current_user=Depends(get_current_user)
):
    db = SessionLocal()

    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        db.close()
        return {
            "message": "Chat not found"
        }

    messages = db.query(Message).filter(
        Message.session_id == session_id
    ).all()

    result = []

    for msg in messages:
        result.append({
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at
        })

    db.close()
    return result


@router.delete("/history/{session_id}")
def delete_history(
    session_id: int,
    current_user=Depends(get_current_user)
):
    db = SessionLocal()

    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        db.close()
        return {
            "message": "Chat not found"
        }

    messages = db.query(Message).filter(
        Message.session_id == session_id
    ).all()

    for msg in messages:
        db.delete(msg)

    db.delete(session)

    db.commit()
    db.close()

    return {
        "message": "Chat deleted successfully"
    }


@router.put("/history/{session_id}")
def rename_history(
    session_id: int,
    request: RenameChatRequest,
    current_user=Depends(get_current_user)
):
    db = SessionLocal()

    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        db.close()
        return {
            "message": "Chat not found"
        }

    session.title = request.title

    db.commit()
    db.close()

    return {
        "message": "Chat title updated successfully"
    }