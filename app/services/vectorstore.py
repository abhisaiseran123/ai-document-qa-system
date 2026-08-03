from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import settings


def get_embedding_function():
    """
    Runs a small open-source embedding model directly in Python (via
    sentence-transformers), rather than calling Ollama. This means
    embeddings work identically on your PC and on a deployed server --
    no external embedding service required.
    """
    return HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)


def get_vectorstore(doc_id: str) -> Chroma:
    return Chroma(
        collection_name=doc_id,
        embedding_function=get_embedding_function(),
        persist_directory=settings.CHROMA_DIR,
    )