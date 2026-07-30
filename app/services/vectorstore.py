from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from app.config import settings


def get_embedding_function():
    """
    Returns the embedding model. This turns text into a list of numbers
    (a vector) that captures its meaning. The SAME model must be used
    both when we store chunks AND when we search later, or comparisons
    won't make sense.
    """
    return OllamaEmbeddings(
        model=settings.EMBEDDING_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
    )


def get_vectorstore(doc_id: str) -> Chroma:
    """
    Loads (or creates) a ChromaDB 'collection' for one specific document.
    Think of a collection like a separate folder/table just for that
    document's chunks -- keeps documents from different users/uploads
    completely separate.
    """
    return Chroma(
        collection_name=doc_id,
        embedding_function=get_embedding_function(),
        persist_directory=settings.CHROMA_DIR,
    )