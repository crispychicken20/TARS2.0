# routes/voice_routes.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import json
import time

router = APIRouter(prefix="/voice", tags=["voice"])

# GLOBAL shared state — updated from wake_word.py
voice_state = {
    "speaking": False,
    "thinking": False,
    "ts": time.time()  # heartbeat timestamp
}

async def event_stream():
    """Server-Sent Events (SSE) pushing TARS voice activity to frontend."""
    while True:
        voice_state["ts"] = time.time()  # helps prevent Safari EventSource timeout

        payload = json.dumps(voice_state)
        yield f"data: {payload}\n\n".encode("utf-8")

        await asyncio.sleep(0.25)  # 4 events per second (smooth animation)

@router.get("/activity")
async def stream_voice_activity():
    return StreamingResponse(event_stream(), media_type="text/event-stream")
