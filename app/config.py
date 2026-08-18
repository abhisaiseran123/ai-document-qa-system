import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # --- Groq (cloud LLM) ---
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    QDRANT_URL: str = os.getenv("QDRANT_URL", "")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")

    # --- Embeddings (local, free, no API needed) ---
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")

    # --- Chunking ---
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 150))

    # --- Retrieval ---
    TOP_K: int = int(os.getenv("TOP_K", 4))

    # --- Storage paths ---
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    CHROMA_DIR: str = os.getenv("CHROMA_DIR", "chroma_db")

settings = Settings()