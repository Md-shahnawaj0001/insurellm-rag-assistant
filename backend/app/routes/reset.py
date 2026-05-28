from fastapi import APIRouter
from app.services.vector_store import collection

router = APIRouter()


@router.post("/reset")
def reset():
    collection.delete(where={})

    return {
        "message": "Knowledge base reset successfully"
    }