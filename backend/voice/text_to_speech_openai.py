"""
text_to_speech_openai.py
------------------------
OpenAI Text-to-Speech for TARS — Final Production Rewrite
"""

import os
import tempfile
from openai import OpenAI
from dotenv import load_dotenv

# Load OpenAI Key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing from .env")

# Initialize client
client = OpenAI(api_key=OPENAI_API_KEY)

# TTS Model + Voice
MODEL = "gpt-4o-mini-tts"
VOICE = "alloy"


def speak_text(text: str):
    """
    Convert text to high-quality speech using OpenAI TTS.
    Saves to a temporary WAV file and plays using macOS 'afplay'.
    """
    if not text or not text.strip():
        return

    try:
        print(f"TARS: {text}")

        # --- FIXED: correct way to get raw audio bytes ---
        response = client.audio.speech.create(
            model=MODEL,
            voice=VOICE,
            input=text
        )

        audio_bytes = response.read()  # <-- critical fix

        # Write bytes to temporary audio file
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp.write(audio_bytes)
        tmp.flush()
        tmp.close()

        # Playback on macOS
        os.system(f"afplay '{tmp.name}'")

    except Exception as e:
        print("TTS ERROR:", e)
