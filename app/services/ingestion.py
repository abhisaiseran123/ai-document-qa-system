import os
import uuid
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.services.vectorstore import get_vectorstore


def _get_loader(file_path: str):
    """Pick the right tool to read text out of the file, based on its extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return PyPDFLoader(file_path)
    elif ext == ".txt":
        return TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def ingest_document(file_path: str) -> tuple[str, int]:
    """
    Full ingestion pipeline:
    1. Load raw text from the file
    2. Split it into small overlapping chunks
    3. Embed each chunk and store it in a new ChromaDB collection
    Returns: (doc_id, number_of_chunks)
    """
    loader = _get_loader(file_path)
    raw_docs = loader.load()

    if not raw_docs or all(not d.page_content.strip() for d in raw_docs):
        raise ValueError("No extractable text found in this document.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(raw_docs)

    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i

    doc_id = str(uuid.uuid4())
    vectorstore = get_vectorstore(doc_id)
    vectorstore.add_documents(chunks)

    return doc_id, len(chunks)