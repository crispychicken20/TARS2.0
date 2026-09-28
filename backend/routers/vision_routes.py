# backend/routers/vision_routes.py
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
import asyncio
import json
import tempfile
import os

from vision.vision_llava import analyze_image
from voice.text_to_speech_openai import speak_text

router = APIRouter(prefix="/vision", tags=["vision"])

# Global vision state, streamed to frontend
vision_state = {
    "active": False,   # camera panel open or not
    "source": None,    # "mac", "phone", etc.
}

# ---------- Helpers so other modules can control vision ----------

def set_vision_state(active: bool, source: str | None = None):
    """
    Called from wake_word or HTTP endpoints to toggle camera mode.
    """
    vision_state["active"] = active
    vision_state["source"] = source


# ---------- SSE stream for frontend ----------

async def vision_event_stream():
    """
    Server-Sent Events: pushes current vision_state ~4x per second.
    """
    while True:
        data = f"data: {json.dumps(vision_state)}\n\n"
        yield data.encode("utf-8")
        await asyncio.sleep(0.25)


@router.get("/state")
async def stream_vision_state():
    """
    Frontend subscribes to /vision/state via EventSource.
    """
    return StreamingResponse(vision_event_stream(), media_type="text/event-stream")


# ---------- Simple open/close endpoints (optional UI buttons) ----------

@router.post("/open")
async def open_vision(source: str = "mac"):
    set_vision_state(True, source)
    return vision_state


@router.post("/close")
async def close_vision():
    set_vision_state(False, None)
    return vision_state


# ---------- Image analysis endpoints ----------

@router.post("/analyze")
async def analyze_frame(file: UploadFile = File(...)):
    """
    Receives an image (PNG/JPEG), runs LLaVA, returns caption.
    """
    suffix = os.path.splitext(file.filename or "")[-1] or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        caption = analyze_image(tmp_path, question="What is happening in this image?")
        return {"caption": caption}
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


@router.post("/analyze-and-speak")
async def analyze_and_speak(file: UploadFile = File(...)):
    """
    Same as /analyze but TARS also speaks the result.
    """
    suffix = os.path.splitext(file.filename or "")[-1] or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        caption = analyze_image(tmp_path, question="Describe what you see.")
        # Speak in a short sentence
        speak_text(f"I see: {caption}")
        return {"caption": caption}
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
