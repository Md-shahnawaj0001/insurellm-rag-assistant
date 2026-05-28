from fastapi import APIRouter, UploadFile, File, Depends
from backend.app.services.rag_service import upload_pdf
from backend.app.dependencies.auth import get_current_user

router = APIRouter()


@router.post("/upload-pdf")
async def upload_pdf_endpoint(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    result = upload_pdf(
        file,
        current_user.id
    )

    return result