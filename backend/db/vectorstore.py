import chromadb
from chromadb.config import Settings as ChromaSettings
from core.config import settings

_client = None

def get_chroma_client():
    global _client
    if _client is None:
        _client = chromadb.Client(ChromaSettings(
            persist_directory=settings.CHROMA_PERSIST_DIR
        ))
    return _client

def get_or_create_collection(name: str, metadata: dict | None = None):
    client = get_chroma_client()
    if not metadata:
        metadata = {"created_by": "tars-backend"}
    return client.get_or_create_collection(name=name, metadata=metadata)

def list_collections():
    client = get_chroma_client()
    return client.list_collections()

def delete_collection(name: str):
    client = get_chroma_client()
    client.delete_collection(name)
