# """
# speech_to_text_eleven.py
# ------------------------
# Speech-to-Text for T.A.R.S. using ElevenLabs STT (Option A)

# - Records one utterance from microphone using PyAudio.
# - Uses RMS VAD to detect user speech and silence.
# - Saves to tmp_audio/tars_utterance.wav
# - Sends WAV to ElevenLabs STT and returns recognized text.
# """

# import os
# import wave
# import math
# import struct
# import time
# from typing import Optional

# import pyaudio
# import requests
# from dotenv import load_dotenv

# # Load env vars
# load_dotenv()

# ELEVEN_API = os.getenv("ELEVENLABS_API_KEY")
# if not ELEVEN_API:
#     raise RuntimeError("ELEVENLABS_API_KEY not set in .env")

# # Audio constants
# RATE = 16000
# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# CHUNK = 1024  # frames per buffer

# # VAD thresholds
# START_THRESHOLD = 300.0     # RMS threshold = speech start
# STOP_THRESHOLD = 200.0      # RMS below this = silence
# MIN_SPEECH_SECONDS = 0.4
# MAX_UTTERANCE_SECONDS = 10.0
# SILENCE_HOLD_SECONDS = 0.7  # how long silence must last to stop


# # ---------------------------------------------------------------
# # Utility: RMS calculation
# # ---------------------------------------------------------------
# def _rms_int16(pcm_bytes: bytes) -> float:
#     """Compute RMS from 16-bit PCM."""
#     if not pcm_bytes:
#         return 0.0
#     count = len(pcm_bytes) // 2
#     if count == 0:
#         return 0.0
#     samples = struct.unpack_from(f"{count}h", pcm_bytes)
#     acc = sum(float(s) * float(s) for s in samples)
#     return math.sqrt(acc / count)


# # ---------------------------------------------------------------
# # RECORD USER SPEECH (VAD)
# # ---------------------------------------------------------------
# def _record_utterance(device_index: Optional[int] = None) -> bytes:
#     """
#     Record one utterance with VAD.
#     Returns PCM bytes, or b"" if nothing captured.
#     """
#     pa = pyaudio.PyAudio()
#     print("[STT] Opening microphone for utterance capture...")

#     stream = pa.open(
#         rate=RATE,
#         channels=CHANNELS,
#         format=FORMAT,
#         input=True,
#         input_device_index=device_index,
#         frames_per_buffer=CHUNK,
#     )

#     frames = []
#     speaking = False
#     start_time = time.time()
#     last_speech_time = None

#     try:
#         print("🎤 Listening… speak now.")
#         while True:
#             data = stream.read(CHUNK, exception_on_overflow=False)
#             rms = _rms_int16(data)

#             now = time.time()
#             elapsed = now - start_time

#             # Wait for speech to start
#             if not speaking:
#                 if rms >= START_THRESHOLD:
#                     speaking = True
#                     last_speech_time = now
#                     frames.append(data)
#                     print(f"[STT] Speech detected (RMS={rms:.1f})")

#             else:
#                 # Record active speech
#                 frames.append(data)
#                 if rms >= STOP_THRESHOLD:
#                     last_speech_time = now

#                 # Stop if too long
#                 if elapsed > MAX_UTTERANCE_SECONDS:
#                     print("[STT] Max speech length reached.")
#                     break

#                 # Stop if silence
#                 if last_speech_time and (now - last_speech_time) > SILENCE_HOLD_SECONDS:
#                     print("[STT] Silence detected → stopping")
#                     break

#             # Auto-stop if no speech at all
#             if not speaking and elapsed > 5.0:
#                 print("[STT] No speech detected within 5s.")
#                 frames = []
#                 break

#     except Exception as e:
#         print(f"[STT] Recording error: {e}")
#         frames = []

#     finally:
#         stream.stop_stream()
#         stream.close()
#         pa.terminate()

#     if not frames:
#         return b""

#     pcm_bytes = b"".join(frames)
#     duration = len(pcm_bytes) / (RATE * 2.0)

#     if duration < MIN_SPEECH_SECONDS:
#         print(f"[STT] Utterance too short ({duration:.2f}s). Ignoring.")
#         return b""

#     print(f"[STT] Captured ~{duration:.2f}s of audio.")
#     return pcm_bytes


# # ---------------------------------------------------------------
# # SAVE WAV
# # ---------------------------------------------------------------
# def _pcm_to_wav(pcm_bytes: bytes, wav_path: str):
#     """Wrap PCM bytes in a WAV container."""
#     os.makedirs(os.path.dirname(wav_path), exist_ok=True)
#     with wave.open(wav_path, "wb") as wf:
#         wf.setnchannels(CHANNELS)
#         wf.setsampwidth(2)
#         wf.setframerate(RATE)
#         wf.writeframes(pcm_bytes)


# # ---------------------------------------------------------------
# # ELEVENLABS TRANSCRIPTION
# # ---------------------------------------------------------------
# def transcribe_once_from_mic(device_index: Optional[int] = None) -> str:
#     """
#     - Record speech with VAD
#     - Save WAV
#     - Send to ElevenLabs STT
#     - Return recognized text
#     """
#     pcm = _record_utterance(device_index)
#     if not pcm:
#         return ""

#     wav_path = os.path.join("tmp_audio", "tars_utterance.wav")
#     _pcm_to_wav(pcm, wav_path)

#     print(f"[STT] Sending WAV to ElevenLabs STT: {wav_path}")

#     url = "https://api.elevenlabs.io/v1/speech-to-text"
#     headers = {"xi-api-key": ELEVEN_API}

#     with open(wav_path, "rb") as f:
#         files = {"file": ("audio.wav", f, "audio/wav")}
#         data = {"model_id": "eleven_multilingual_v2"}

#         try:
#             r = requests.post(url, headers=headers, files=files, data=data)
#             r.raise_for_status()
#             text = r.json().get("text", "").strip()
#             print(f"[STT ✅] Recognized: {text}")
#             return text
#         except Exception as e:
#             print(f"[STT ❌] ElevenLabs STT error: {e}")
#             return ""
