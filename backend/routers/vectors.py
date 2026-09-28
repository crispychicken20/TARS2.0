# backend/routers/vectors.py
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from db.vectorstore import (
    get_or_create_collection,
    list_collections,
    delete_collection,
)
from services.embeddings_service import embed_texts
from services.chunker import simple_overlap_chunk

router = APIRouter(prefix="/vectors", tags=["vectors"])

# ---------------------------
# Inline Schemas (local-only)
# ---------------------------

class CreateCollectionRequest(BaseModel):
    name: str
    metadata: Optional[Dict[str, Any]] = None

class CollectionInfo(BaseModel):
    name: str
    metadata: Optional[Dict[str, Any]] = None
    count: Optional[int] = None  # best-effort; may be None for speed

class UpsertItem(BaseModel):
    id: str
    text: str
    metadata: Optional[Dict[str, Any]] = None
    document_id: Optional[str] = None

class UpsertRequest(BaseModel):
    collection: str
    items: List[UpsertItem]
    chunk: bool = True

class QueryRequest(BaseModel):
    collection: str
    query: str
    top_k: int = Field(5, ge=1, le=50)
    where: Optional[Dict[str, Any]] = None

class QueryResult(BaseModel):
    id: str
    text: str
    score: float
    metadata: Optional[Dict[str, Any]] = None
    document_id: Optional[str] = None

class QueryResponse(BaseModel):
    results: List[QueryResult]


# ---------------
# Route Handlers
# ---------------

@router.get("/collections", response_model=List[CollectionInfo])
def get_collections():
    """
    List collections. We avoid calling .count() on each to keep this fast.
    If you want counts, uncomment the try/except block below.
    """
    cols = list_collections()
    out: List[CollectionInfo] = []

    for c in cols:
        info = CollectionInfo(name=c.name, metadata=c.metadata, count=None)

        # Optional: get count (slower for many collections)
        # try:
        #     info.count = c.count()  # some Chroma versions support c.count()
        # except Exception:
        #     info.count = None

        out.append(info)

    return out


@router.post("/collections", response_model=CollectionInfo)
def create_collection(req: CreateCollectionRequest):
    col = get_or_create_collection(req.name, req.metadata)
    # Optional: attempt to fetch count after creation
    count_val: Optional[int] = None
    # try:
    #     count_val = col.count()
    # except Exception:
    #     pass

    return CollectionInfo(name=col.name, metadata=col.metadata, count=count_val)


@router.delete("/collections/{name}")
def remove_collection(name: str):
    delete_collection(name)
    return {"status": "deleted", "name": name}


@router.post("/upsert")
def upsert(req: UpsertRequest):
    """
    Upserts raw text items. If chunk=True, we split long texts into overlapping chunks.
    """
    col = get_or_create_collection(req.collection)

    ids: List[str] = []
    docs: List[str] = []
    metas: List[Dict[str, Any]] = []

    for item in req.items:
        if req.chunk:
            chunks = simple_overlap_chunk(item.text)
            for idx, ch in enumerate(chunks):
                ids.append(f"{item.id}::chunk::{idx}")
                docs.append(ch)

                meta = dict(item.metadata) if item.metadata else {}
                if item.document_id:
                    meta["document_id"] = item.document_id
                meta["chunk_index"] = idx
                metas.append(meta)
        else:
            ids.append(item.id)
            docs.append(item.text)

            meta = dict(item.metadata) if item.metadata else {}
            if item.document_id:
                meta["document_id"] = item.document_id
            metas.append(meta)

    if not docs:
        raise HTTPException(status_code=400, detail="No text to upsert.")

    embeddings = embed_texts(docs)
    col.upsert(ids=ids, documents=docs, embeddings=embeddings, metadatas=metas)

    return {"status": "ok", "upserted": len(ids)}


@router.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    """
    Semantic query over a collection.
    """
    col = get_or_create_collection(req.collection)
    query_emb = embed_texts([req.query])[0]

    q = col.query(
        query_embeddings=[query_emb],
        n_results=req.top_k,
        where=req.where
    )

    # Defensive checks—Chroma returns lists-of-lists
    ids = q.get("ids", [[]])[0]
    docs = q.get("documents", [[]])[0]
    dists = q.get("distances", [[]])[0] if "distances" in q else [0.0] * len(ids)
    metas = q.get("metadatas", [[]])[0] if q.get("metadatas") else [None] * len(ids)

    results: List[QueryResult] = []
    for i in range(len(ids)):
        metadata = metas[i] if isinstance(metas, list) and i < len(metas) else None
        document_id = None
        if isinstance(metadata, dict):
            document_id = metadata.get("document_id")

        results.append(QueryResult(
            id=ids[i],
            text=docs[i],
            score=float(dists[i]) if i < len(dists) else 0.0,
            metadata=metadata,
            document_id=document_id
        ))

    return QueryResponse(results=results)
