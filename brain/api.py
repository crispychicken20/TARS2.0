# import uvicorn
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import List, Optional, Dict, Any
# from brain import end_point_chat_tars

# # Import your TARS chat logic
# # from brain import graph   # already initialized in brain.py
# # from brain_endpoint import end_point_chat_tars  # assuming your method is in brain_endpoint.py
# # For this example, we’ll assume end_point_chat_tars is defined in the same file.

# app = FastAPI(title="TARS Chat API", version="1.0")

# # ----------- Request / Response Models -----------
# class Message(BaseModel):
#     role: str
#     content: str

# class ChatRequest(BaseModel):
#     question: str
#     session_id: str
#     user_id: str
#     conversation_history: Optional[List[Message]] = None

# class ChatResponse(BaseModel):
#     response: str
#     status: str
#     session_id: str
#     user_id: str


# # ----------- FastAPI Endpoint -----------
# @app.post("/chat", response_model=ChatResponse)
# async def chat_endpoint(payload: ChatRequest):
#     """
#     FastAPI endpoint that routes user messages to the TARS chat engine.
#     """
#     try:
#         result = end_point_chat_tars(
#             question=payload.question,
#             session_id=payload.session_id,
#             user_id=payload.user_id,
#             conversation_history=[m.dict() for m in (payload.conversation_history or [])]
#         )

#         return ChatResponse(**result)

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# # Optional root route
# @app.get("/")
# def root():
#     return {"message": "TARS Chat API is running 🚀"}

# # local run
# if __name__ == "__main__":
#     import os

#     port = int(os.getenv("PORT", 8080))  # Cloud Run will set PORT, fallback to 8080 locally

#     uvicorn.run("api:app", host="0.0.0.0", port=port, reload=True)