from typing import List, Dict, Any
from db.vectorstore import get_or_create_collection
from services.embeddings_service import embed_texts

def hybrid_retrieval(collection_name: str, query: str, top_k: int = 5, where: Dict[str, Any] | None = None):
    col = get_or_create_collection(collection_name)
    query_emb = embed_texts([query])[0]
    q = col.query(
        query_embeddings=[query_emb],
        n_results=top_k,
        where=where
    )
    # Normalize response
    results = []
    for i in range(len(q["ids"][0])):
        results.append({
            "id": q["ids"][0][i],
            "text": q["documents"][0][i],
            "score": float(q["distances"][0][i]) if "distances" in q else 0.0,
            "metadata": q["metadatas"][0][i] if q["metadatas"] else None,
            "document_id": q["metadatas"][0][i].get("document_id") if q["metadatas"] and q["metadatas"][0][i] else None
        })
    return results

def synthesize_answer(question: str, context_chunks: List[str]) -> str:
    # Placeholder: concise extractive-style synthesis; swap with LLM call later
    joined = "\n\n".join(context_chunks[:3])
    return (
        "Draft answer (no LLM yet):\n"
        f"Q: {question}\n\n"
        "Relevant context (top):\n"
        f"{joined}\n\n"
        "→ Integrate an LLM here to produce a final answer."
    )
