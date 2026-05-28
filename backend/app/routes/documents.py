from fastapi import APIRouter, Depends
from backend.app.db.database import SessionLocal
from backend.app.db.models import Document
from backend.app.dependencies.auth import get_current_user

router = APIRouter()


@router.get("/documents")
def get_documents(current_user=Depends(get_current_user)):
    db = SessionLocal()

    documents = db.query(Document).filter(
        Document.user_id == current_user.id
    ).all()

    result = []

    for doc in documents:
        result.append({
            "id": doc.id,
            "filename": doc.filename,
            "chunk_count": doc.chunk_count,
            "uploaded_at": doc.uploaded_at
        })

    db.close()
    return result


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    current_user=Depends(get_current_user)
):
    db = SessionLocal()

    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not document:
        db.close()
        return {
            "message": "Document not found"
        }

    db.delete(document)
    db.commit()
    db.close()

    return {
        "message": "Document deleted successfully"
    }