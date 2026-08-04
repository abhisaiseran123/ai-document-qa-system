from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from app.config import settings


def get_embedding_function():
    """
    Google's hosted embedding API. output_dimensionality is fixed at 768
    here so it always matches the Qdrant collection's vector size below.
    """
    return GoogleGenerativeAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        output_dimensionality=768,
    )


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)


def get_vectorstore(doc_id: str) -> QdrantVectorStore:
    """
    Same one-collection-per-document pattern as before, just backed by
    Qdrant Cloud instead of a local ChromaDB file. This removes the
    onnxruntime dependency entirely, fixing the Render memory crash.
    """
    client = get_qdrant_client()
    embedding = get_embedding_function()

    if not client.collection_exists(doc_id):
        client.create_collection(
            collection_name=doc_id,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )

    return QdrantVectorStore(
        client=client,
        collection_name=doc_id,
        embedding=embedding,
    )