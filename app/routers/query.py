from fastapi import APIRouter, HTTPException

from app.models.schemas import AskRequest, AskResponse, SourceChunk
from app.services.rag_chain import answer_question

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        answer, source_docs = answer_question(request.doc_id, request.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {e}")

    sources = [
        SourceChunk(
            content=doc.page_content,
            chunk_index=doc.metadata.get("chunk_index", -1),
        )
        for doc in source_docs
    ]

    return AskResponse(answer=answer, sources=sources)