from services.rag_services import hybrid_retrieval, synthesize_answer


from pydantic import BaseModel
from typing import List

class RagRequest(BaseModel):
    collection: str
    question: str
    top_k: int = 5

class RagResponse(BaseModel):
    question: str
    context: List[str]
    synthesized_answer: str
    
from fastapi import APIRouter, HTTPException
router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/rag", response_model=RagResponse)
def rag(req: RagRequest):
    hits = hybrid_retrieval(req.collection, req.question, req.top_k)
    context = [h["text"] for h in hits]
    answer = synthesize_answer(req.question, context)
    return RagResponse(question=req.question, context=context, synthesized_answer=answer)
