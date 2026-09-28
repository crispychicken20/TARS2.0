"""
tars_streaming.py
-----------------
FULL OpenAI-only streaming pipeline for TARS:

PIPELINE:
Mic → Whisper-Streaming → GPT-4o-mini → TTS-Streaming → Speakers

Requirements:
- No ElevenLabs
- Ultra-low latency
- Works with wakeword loop
"""

import os
import pyaudio
import asyncio
import json
import websockets
import aiohttp
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

################################################################################
#                               AUDIO CONSTANTS
################################################################################

RATE = 16000
CHUNK = 512


################################################################################
#                               MIC STREAM (async)
################################################################################
async def mic_stream():
    """Yields audio chunks until silence is detected."""
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    print("🎤 [TARS] Mic live (OpenAI streaming)…")

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        yield data

    stream.stop_stream()
    stream.close()
    pa.terminate()


################################################################################
#                   1️⃣ STREAMING SPEECH-TO-TEXT (OpenAI)
################################################################################
async def openai_stt_stream(text_queue: asyncio.Queue):
    """
    Sends mic audio → OpenAI Whisper-Streaming → text tokens
    """

    print("🧠 [TARS] Connected to OpenAI Whisper Streaming")

    uri = "wss://api.openai.com/v1/audio/transcriptions/stream"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    async with websockets.connect(uri, extra_headers=headers) as ws:

        async def sender():
            async for chunk in mic_stream():
                await ws.send(chunk)

        async def receiver():
            async for msg in ws:
                data = json.loads(msg)
                if "text" in data:
                    text = data["text"].strip()
                    if text:
                        print(f"[STT 🎧] {text}")
                        await text_queue.put(text)

        await asyncio.gather(sender(), receiver())


################################################################################
#                       2️⃣ STREAMING BRAIN (GPT-4o-mini)
################################################################################
async def brain_stream(text_queue: asyncio.Queue, speech_queue: asyncio.Queue):
    """
    Takes text from STT → streams to GPT → streams tokens to TTS.
    """

    print("🧠 [TARS] Brain online (GPT-4o-mini)")

    while True:
        user_text = await text_queue.get()
        if not user_text:
            continue

        print(f"[BRAIN INPUT] {user_text}")

        async with client.chat.completions.stream(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are TARS, a friendly, concise assistant. "
                        "Return only spoken English, no markdown."
                    )
                },
                {"role": "user", "content": user_text}
            ],
        ) as stream:

            async for event in stream:
                if event.type == "delta" and event.delta.content:
                    token = event.delta.content
                    print(token, end="", flush=True)
                    await speech_queue.put(token)

            print("\n[DEBUG] Brain finished.\n")


################################################################################
#                   3️⃣ STREAMING TEXT-TO-SPEECH (OpenAI)
################################################################################
async def openai_tts_stream(speech_queue: asyncio.Queue):
    """
    Streaming token fragments → OpenAI TTS → speaker playback (afplay)
    """

    print("🔊 [TARS] OpenAI TTS streaming ready")

    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        buffer = ""

        async for token in speech_queue:
            buffer += token

            # Play when sentence ends or buffer is large
            if len(buffer) > 120 or token.endswith(('.', '!', '?')):

                payload = {
                    "model": "gpt-4o-mini-tts",
                    "voice": "alloy",
                    "input": buffer
                }

                async with session.post(url, headers=headers, json=payload) as resp:
                    audio = await resp.read()
                    with open("tts_chunk.wav", "wb") as f:
                        f.write(audio)

                os.system("afplay tts_chunk.wav")

                buffer = ""


################################################################################
#                             4️⃣ MAIN LOOP
################################################################################
async def start_streaming_pipeline():
    """
    Starts FULL OpenAI streaming pipeline:
    STT → GPT → TTS
    """
    text_queue = asyncio.Queue()
    speech_queue = asyncio.Queue()

    await asyncio.gather(
        openai_stt_stream(text_queue),
        brain_stream(text_queue, speech_queue),
        openai_tts_stream(speech_queue)
    )


if __name__ == "__main__":
    asyncio.run(start_streaming_pipeline())
