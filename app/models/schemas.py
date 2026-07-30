from pydantic import BaseModel
from typing import List


class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    num_chunks: int
    message: str


class AskRequest(BaseModel):
    doc_id: str
    question: str


class SourceChunk(BaseModel):
    content: str
    chunk_index: int


class AskResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]