from fastapi import FastAPI
from app.routers import upload, query

app = FastAPI(
    title="AI Document Question Answering System",
    description="Upload a document, then ask questions about it using RAG.",
    version="1.0.0",
)

app.include_router(upload.router, tags=["Upload"])
app.include_router(query.router, tags=["Query"])


@app.get("/")
async def health_check_root():
    return {"status": "ok", "message": "AI Document QA API is running"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}