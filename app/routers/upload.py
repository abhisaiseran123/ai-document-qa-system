import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.config import settings
from app.models.schemas import UploadResponse
from app.services.ingestion import ingest_document

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".txt"}


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {ALLOWED_EXTENSIONS}",
        )

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    saved_path = os.path.join(settings.UPLOAD_DIR, file.filename)

    with open(saved_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        doc_id, num_chunks = ingest_document(saved_path)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

    return UploadResponse(
        doc_id=doc_id,
        filename=file.filename,
        num_chunks=num_chunks,
        message="Document ingested successfully. Use the doc_id to ask questions.",
    )