"""
app.py
------
Minimal entry point for the TARS backend.
Routes imported from /routers (wakeword, voice).
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from core.config import settings
from core.logging import setup_logging
from routers import wakeword, voice
from routers.dots_routes import router as voice_router
from routers.vision_routes import router as vision_router



load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
logger = setup_logging()

app = FastAPI(title="TARS Backend", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(wakeword.router)
app.include_router(voice.router)
app.include_router(voice_router)
app.include_router(vision_router)

@app.get("/")
def root():
    return {"service": "TARS Backend", "status": "running"}

def run():
    import uvicorn
    uvicorn.run(
        "app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_DEBUG
    )

if __name__ == "__main__":
    run()
