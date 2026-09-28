"""
wakeword.py
------------
Router connecting the frontend endpoints with wake_word logic.
"""

from fastapi import APIRouter
from wake_word.wake_word import start_background_listener, get_status, stop_listener

router = APIRouter(prefix="/wakeword", tags=["wakeword"])

@router.post("/start")
def start():
    """Starts continuous background listening."""
    return start_background_listener()

@router.get("/status")
def status():
    """Frontend polls this route to detect wakeword status."""
    return get_status()

@router.post("/stop")
def stop():
    """Stops wakeword listening loop."""
    return stop_listener()
