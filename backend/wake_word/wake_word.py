"""Local Vosk activation for TARS.

Drop-in replacement for backend/wake_word/wake_word.py.
Based on TARS2.0 wake_word.py at 95adb366fc475a96a9d07e447c3518b8dc0e6647.
Keep the existing OpenAI speech and brain modules.

backend/.env:
    VOSK_MODEL_PATH=models/vosk-model-small-en-us-0.15
    WAKE_PHRASES=hey tars,hey stars
    TARS_DEBUG=1

"hey stars" is a configurable recognition alias, and will also activate TARS
if spoken literally. Set WAKE_PHRASES=hey tars for strict phrase matching.
No Picovoice key or .ppn model is used by this module.
"""

import json
import os
import re
import threading
import time
from pathlib import Path

import pyaudio
from dotenv import load_dotenv
from vosk import KaldiRecognizer, Model

BACKEND_DIR = Path(__file__).resolve().parents[1]
# Load configuration before importing modules that require OPENAI_API_KEY.
load_dotenv(BACKEND_DIR / ".env")
load_dotenv(BACKEND_DIR.parent / ".env")

from brain.brain_manager import ask_brain
from voice.text_to_speech_openai import speak_text
from voice.speech_to_text_openai import transcribe_once_from_mic
from routers.vision_routes import set_vision_state
from routers.dots_routes import voice_state

_model_path = Path(os.getenv(
    "VOSK_MODEL_PATH", "models/vosk-model-small-en-us-0.15"
)).expanduser()
MODEL_PATH = _model_path if _model_path.is_absolute() else BACKEND_DIR / _model_path
DEBUG = os.getenv("TARS_DEBUG", "0").lower() in ("1", "true", "yes")
RATE = 16000
CHUNK = 1024


def _normalize(text):
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


WAKE_PHRASES = tuple(
    phrase for item in os.getenv("WAKE_PHRASES", "hey tars,hey stars").split(",")
    if (phrase := _normalize(item))
)


def _matches_wake_phrase(text):
    padded = " " + _normalize(text) + " "
    return any(" " + phrase + " " in padded for phrase in WAKE_PHRASES)


def dbg(msg):
    if DEBUG:
        print(f"[TARS::Vosk] {msg}")


_stop_event = threading.Event()
_state_lock = threading.Lock()
thread = None
_last_error = None
_detected_until = 0.0


class WakeWordSystem:
    """Recognize a configured activation phrase from local microphone audio."""

    def __init__(self):
        self.pa = None
        self.stream = None
        if not WAKE_PHRASES:
            raise ValueError("Set WAKE_PHRASES to at least one non-empty phrase.")
        if not (MODEL_PATH / "am" / "final.mdl").is_file():
            raise FileNotFoundError(
                f"Vosk model not found at {MODEL_PATH}. "
                "Set VOSK_MODEL_PATH to the extracted model directory."
            )
        dbg(f"Loading local model: {MODEL_PATH}")
        self.model = Model(str(MODEL_PATH))
        try:
            self.pa = pyaudio.PyAudio()
            self.device_index = self._pick_mic()
            self.stream = self._open()
        except Exception:
            self.cleanup()
            raise

    def _pick_mic(self):
        configured = os.getenv("MIC_DEVICE_INDEX")
        if configured:
            index = int(configured)
            info = self.pa.get_device_info_by_index(index)
            if info.get("maxInputChannels", 0) < 1:
                raise ValueError(f"Microphone device {index} has no input channels.")
            return index
        # Respect the microphone selected in macOS sound settings.
        return int(self.pa.get_default_input_device_info()["index"])

    def _open(self):
        # New recognizer discards the previous session's activation audio.
        self.recognizer = KaldiRecognizer(self.model, RATE)
        dbg(f"Opening microphone #{self.device_index}; phrases: {WAKE_PHRASES}")
        return self.pa.open(
            rate=RATE, channels=1, format=pyaudio.paInt16,
            input=True, input_device_index=self.device_index,
            frames_per_buffer=CHUNK,
        )

    def listen(self):
        """Wait for a complete activation utterance or a stop request."""
        global _detected_until
        dbg("Standby: say 'Hey TARS', then pause.")
        while not _stop_event.is_set():
            pcm = self.stream.read(CHUNK, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(pcm):
                text = json.loads(self.recognizer.Result()).get("text", "")
                if text:
                    dbg(f"Heard: {text}")
                if _matches_wake_phrase(text):
                    _detected_until = time.monotonic() + 4.0
                    return True
        return False

    def close_stream(self):
        stream, self.stream = self.stream, None
        if stream is not None:
            try:
                stream.stop_stream()
            finally:
                stream.close()

    def cleanup(self):
        try:
            self.close_stream()
        finally:
            pa, self.pa = self.pa, None
            if pa is not None:
                pa.terminate()


def _conversation_loop(w):
    while not _stop_event.is_set():
        # ------------------------------------------------------------
        # 1. WAIT FOR WAKE WORD
        # ------------------------------------------------------------
        if not w.listen():
            return
        # Release the microphone before speech playback and command recording.
        w.close_stream()

        # FRONTEND STATE: speaking
        voice_state["speaking"] = True
        voice_state["thinking"] = False

        speak_text("Hey, how can I help you?")

        # Reset to idle
        voice_state["speaking"] = False
        voice_state["thinking"] = False

        
        # Track if we're waiting for camera choice
        pending_camera_choice = False

        # ------------------------------------------------------------
        # 2. CONVERSATION LOOP
        # ------------------------------------------------------------
        while not _stop_event.is_set():

            dbg("Listening for user speech…")

            # User speaking → audio activity
            voice_state["speaking"] = True
            voice_state["thinking"] = False

            query = transcribe_once_from_mic(device_index=w.device_index)
            if _stop_event.is_set():
                return

            # User finished speaking → idle/thinking soon
            voice_state["speaking"] = False

            if not query.strip():
                voice_state["thinking"] = False
                speak_text("Umm Sorry, I didn't catch that.")
                continue

            # Exit signal
            if "bye tars" in query.lower():
                voice_state["thinking"] = False
                speak_text("Goodbye, going back to standby.")
                break
            
            lower = query.lower()
            camera_intents = [
                "open the camera", "open camera", "start camera", "start the camera",
                "camera on", "turn on camera", "turn camera on",
                "vision mode", "enable vision", "use camera", "show camera",
                "start video", "video mode", "look at me", "see me"
            ]

            if any(phrase in lower for phrase in camera_intents):
                speak_text("Which camera should I use? Say 'MacBook' or 'Phone'.")
                pending_camera_choice = True
                continue

            # ---------- CAMERA CHOICE (NO LLM INVOLVEMENT) ----------
            if pending_camera_choice:
                if "phone" in lower:
                    speak_text("Opening your phone camera.")
                    set_vision_state(True, "phone")
                    pending_camera_choice = False
                    continue

                if "mac" in lower or "laptop" in lower or "computer" in lower:
                    speak_text("Opening your MacBook camera.")
                    set_vision_state(True, "mac")
                    pending_camera_choice = False
                    continue

                # If unclear:
                speak_text("Please say clearly: MacBook or Phone.")
                continue

            # ---------- CLOSE CAMERA ----------
            if "close camera" in lower or "stop camera" in lower or "stop looking" in lower:
                speak_text("Closing the camera view.")
                set_vision_state(False, None)
                continue
    
            # --------------------------------------------------------
            # THINKING MODE
            # --------------------------------------------------------
            voice_state["thinking"] = True

            reply = ask_brain(query)

            # Done thinking
            voice_state["thinking"] = False

            # --------------------------------------------------------
            # SPEAKING MODE
            # --------------------------------------------------------
            voice_state["speaking"] = True
            speak_text(reply)
            voice_state["speaking"] = False

        # ------------------------------------------------------------
        # 3. RETURN TO WAKEWORD MODE
        # ------------------------------------------------------------
        dbg("Re-opening wakeword microphone")
        voice_state["speaking"] = False
        voice_state["thinking"] = False

        if not _stop_event.is_set():
            w.stream = w._open()


def _loop():
    global _last_error, _detected_until
    w = None
    try:
        w = WakeWordSystem()
        _conversation_loop(w)
    except Exception as exc:
        _last_error = f"{type(exc).__name__}: {exc}"
        print(f"[TARS::Vosk] Listener failed: {_last_error}")
    finally:
        try:
            if w is not None:
                w.cleanup()
        finally:
            _detected_until = 0.0
            voice_state["speaking"] = False
            voice_state["thinking"] = False


def start_background_listener():
    global thread, _last_error, _detected_until
    with _state_lock:
        if thread and thread.is_alive():
            return {"status": "stopping" if _stop_event.is_set() else "already_running"}
        _stop_event.clear()
        _last_error = None
        _detected_until = 0.0
        thread = threading.Thread(target=_loop, daemon=True)
        thread.start()
    return {"status": "started"}


def get_status():
    running = bool(thread and thread.is_alive())
    status = "stopping" if running and _stop_event.is_set() else (
        "running" if running else "stopped"
    )
    return {
        "status": status,
        "detected": running and time.monotonic() < _detected_until,
        "error": _last_error,
    }


def stop_listener():
    # Cooperatively stops after any in-flight STT/LLM/TTS operation finishes.
    with _state_lock:
        _stop_event.set()
    return get_status()

