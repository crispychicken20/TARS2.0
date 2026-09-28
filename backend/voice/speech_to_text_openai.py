"""
speech_to_text_openai.py
------------------------
OpenAI Whisper STT for T.A.R.S.
- Records one utterance using VAD
- Converts to WAV
- Sends to OpenAI Whisper
"""

import os
import time
import math
import struct
import wave
import pyaudio
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing from .env")

client = OpenAI(api_key=OPENAI_API_KEY)

# Audio constants
RATE = 16000
FORMAT = pyaudio.paInt16
CHANNELS = 1
CHUNK = 1024

# VAD thresholds
START_THRESHOLD = 250
STOP_THRESHOLD = 180
SILENCE_HOLD = 0.7
MAX_UTTERANCE = 10.0
MIN_UTTERANCE = 0.4


def _rms(pcm: bytes) -> float:
    if not pcm:
        return 0.0
    count = len(pcm) // 2
    samples = struct.unpack_from(f"{count}h", pcm)
    return math.sqrt(sum(s * s for s in samples) / count)


def transcribe_once_from_mic(device_index: Optional[int] = None) -> str:
    """Record 1 utterance → transcribe with OpenAI Whisper."""
    pa = pyaudio.PyAudio()

    stream = pa.open(
        rate=RATE, channels=CHANNELS, format=FORMAT,
        input=True, input_device_index=device_index,
        frames_per_buffer=CHUNK
    )

    print("🎤 Listening… speak now.")

    frames = []
    speaking = False
    start = time.time()
    last_voice = None

    try:
        while True:
            pcm = stream.read(CHUNK, exception_on_overflow=False)
            rms = _rms(pcm)
            now = time.time()

            if not speaking:
                if rms > START_THRESHOLD:
                    speaking = True
                    last_voice = now
                    frames.append(pcm)
                    print(f"[STT] Speech detected (RMS={rms:.1f})")
            else:
                frames.append(pcm)
                if rms > STOP_THRESHOLD:
                    last_voice = now

                if now - start > MAX_UTTERANCE:
                    print("[STT] Max length reached.")
                    break

                if last_voice and (now - last_voice) > SILENCE_HOLD:
                    print("[STT] Silence → end utterance.")
                    break

            if not speaking and (now - start) > 5:
                print("[STT] No speech → abort.")
                frames = []
                break

    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()

    if not frames:
        return ""

    audio = b"".join(frames)
    duration = len(audio) / (RATE * 2)
    if duration < MIN_UTTERANCE:
        print("[STT] Too short.")
        return ""

    os.makedirs("tmp_audio", exist_ok=True)
    wav_path = "tmp_audio/tars_utterance.wav"

    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(audio)

    print("[STT] Sending to OpenAI Whisper…")

    try:
        with open(wav_path, "rb") as f:
            rsp = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=f,
            )
        text = (rsp.text or "").strip()
        print("[STT OK]", text)
        return text
    except Exception as e:
        print("[STT ERROR]", e)
        return ""
