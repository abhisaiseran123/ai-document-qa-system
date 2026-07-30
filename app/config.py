import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Ollama connection
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3.1")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

    # Chunking settings
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 150))

    # Retrieval settings
    TOP_K: int = int(os.getenv("TOP_K", 4))

    # Storage paths
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    CHROMA_DIR: str = os.getenv("CHROMA_DIR", "chroma_db")

settings = Settings()