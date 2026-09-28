from fastapi import APIRouter
from voice.speech_to_text_openai import transcribe_once_from_mic
from voice.text_to_speech_openai import speak_text

router = APIRouter(prefix="/voice", tags=["voice"])

@router.post("/stt")
def stt(device_index: int = 0):
    try:
        text = transcribe_once_from_mic(device_index=device_index)
        return {"text": text}
    except Exception as e:
        return {"error": str(e)}

@router.post("/tts")
def tts(payload: dict):
    try:
        speak_text(payload.get("text", ""))
        return {"status": "ok"}
    except Exception as e:
        return {"error": str(e)}
