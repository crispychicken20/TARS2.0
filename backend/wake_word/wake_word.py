# """
# wake_word.py
# -------------
# Wake Word Detection and Conversation Logic for T.A.R.S.
# Now using OpenAI-based STT (Option A).
# """

# import os
# import struct
# import threading
# import time
# import math

# import pyaudio
# import pvporcupine
# from dotenv import load_dotenv

# from brain.brain_manager import ask_brain
# from voice.text_to_speech_eleven import speak_text
# from voice.speech_to_text_eleven import transcribe_once_from_mic

# load_dotenv()

# ACCESS_KEY = os.getenv("ACCESS_KEY")
# KEYWORD_PATH = os.getenv("KEYWORD_PATH", "models/HEY-TARS_en_mac_v3_0_0.ppn")
# TARS_DEBUG = os.getenv("TARS_DEBUG", "0").lower() in ("1", "true", "yes")

# wake_system = None
# wake_thread = None
# detected_flag = False
# conversation_active = False
# shutdown_flag = False


# def _dbg(msg: str):
#     if TARS_DEBUG:
#         ts = time.strftime("%H:%M:%S")
#         print(f"[DEBUG {ts}] {msg}")


# def _rms_int16(pcm_bytes: bytes) -> float:
#     """Compute RMS of 16-bit PCM buffer."""
#     if not pcm_bytes:
#         return 0.0
#     count = len(pcm_bytes) // 2
#     if count == 0:
#         return 0.0
#     samples = struct.unpack_from(f"{count}h", pcm_bytes)
#     acc = 0.0
#     for s in samples:
#         acc += float(s) * float(s)
#     return math.sqrt(acc / count)


# class WakeWordSystem:
#     """Porcupine-based passive listener for 'Hey TARS'."""

#     def __init__(self, keyword_path: str, access_key: str):
#         self.keyword_path = keyword_path
#         self.access_key = access_key
#         self.porcupine = None
#         self.pa = None
#         self.audio_stream = None
#         self.active = False
#         self.device_index = None

#     def list_devices(self):
#         pa = pyaudio.PyAudio()
#         devices = []
#         for i in range(pa.get_device_count()):
#             info = pa.get_device_info_by_index(i)
#             if info.get("maxInputChannels", 0) > 0:
#                 devices.append({"index": i, "name": info["name"]})
#         pa.terminate()
#         return devices

#     def select_device(self):
#         """Pick a reasonable input mic."""
#         pa = self.pa or pyaudio.PyAudio()
#         try:
#             fallback = pa.get_default_input_device_info()["index"]
#         except Exception:
#             _dbg("No default input device available.")
#             raise

#         preferred = None
#         for i in range(pa.get_device_count()):
#             name = pa.get_device_info_by_index(i)["name"]
#             if "Microphone" in name or "MacBook" in name or "External" in name:
#                 preferred = i
#                 break

#         chosen = preferred if preferred is not None else fallback
#         self.device_index = chosen
#         _dbg(f"Selected input device: [{chosen}] {pa.get_device_info_by_index(chosen)['name']}")
#         return chosen

#     def setup(self):
#         """Initialize Porcupine and open microphone stream."""
#         try:
#             _dbg("Initializing Porcupine wake-word engine...")
#             self.porcupine = pvporcupine.create(
#                 access_key=self.access_key,
#                 keyword_paths=[self.keyword_path],
#             )
#         except Exception as e:
#             print(f"Porcupine init failed: {e}")
#             self.porcupine = None
#             return

#         if not self.porcupine:
#             print("Wake-word model creation failed.")
#             return

#         if self.pa is None:
#             self.pa = pyaudio.PyAudio()
#         self.select_device()
#         self._open_stream()
#         self.active = True
#         print("Wake-word system ready. Say 'Hey TARS'.")

#     def _open_stream(self):
#         if not self.porcupine:
#             return

#         if self.pa is None:
#             self.pa = pyaudio.PyAudio()

#         if self.audio_stream:
#             try:
#                 self.audio_stream.stop_stream()
#                 self.audio_stream.close()
#             except Exception:
#                 pass

#         try:
#             self.audio_stream = self.pa.open(
#                 rate=self.porcupine.sample_rate,
#                 channels=1,
#                 format=pyaudio.paInt16,
#                 input=True,
#                 input_device_index=self.device_index,
#                 frames_per_buffer=self.porcupine.frame_length,
#             )
#             _dbg(f"Audio stream opened on device #{self.device_index} at {self.porcupine.sample_rate} Hz")
#         except Exception as e:
#             print(f"Audio stream open error: {e}")
#             # fallback
#             try:
#                 self.select_device()
#                 self.audio_stream = self.pa.open(
#                     rate=self.porcupine.sample_rate,
#                     channels=1,
#                     format=pyaudio.paInt16,
#                     input=True,
#                     input_device_index=self.device_index,
#                     frames_per_buffer=self.porcupine.frame_length,
#                 )
#                 _dbg(f"Fallback mic opened: #{self.device_index}")
#             except Exception as e2:
#                 print(f"Fallback open error: {e2}")
#                 self.audio_stream = None

#     def listen(self) -> bool:
#         """Block until wake word detected or error."""
#         frame_count = 0
#         last_level_log = 0.0
#         while True:
#             try:
#                 if not self.audio_stream or not self.audio_stream.is_active():
#                     _dbg("Audio stream inactive. Reopening...")
#                     self.select_device()
#                     self._open_stream()
#                     time.sleep(0.05)
#                     continue

#                 pcm_bytes = self.audio_stream.read(
#                     self.porcupine.frame_length, exception_on_overflow=False
#                 )

#                 if TARS_DEBUG:
#                     rms = _rms_int16(pcm_bytes)
#                     now = time.time()
#                     if now - last_level_log > 0.1:
#                         _dbg(f"Mic RMS={rms:.1f}")
#                         last_level_log = now

#                 pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm_bytes)
#                 result = self.porcupine.process(pcm)
#                 frame_count += 1

#                 if result >= 0:
#                     _dbg(f"Wake word detected at frame={frame_count}")
#                     return True

#             except Exception as e:
#                 print(f"Audio error: {e}")
#                 time.sleep(0.2)
#                 self._open_stream()

#     def reset(self):
#         """Re-open mic after conversation."""
#         _dbg("Resetting listener.")
#         self._open_stream()

#     def cleanup(self):
#         """Release audio and Porcupine resources."""
#         try:
#             if self.audio_stream:
#                 self.audio_stream.stop_stream()
#                 self.audio_stream.close()
#         except Exception:
#             pass
#         if self.pa:
#             self.pa.terminate()
#             self.pa = None
#         if self.porcupine:
#             self.porcupine.delete()
#             self.porcupine = None
#         _dbg("Audio cleaned up.")


# # -------------------------------------------------------------
# # Wakeword loop with conversation
# # -------------------------------------------------------------
# def _wakeword_loop():
#     global detected_flag, conversation_active, shutdown_flag
#     while not shutdown_flag:
#         try:
#             _dbg("Waiting for wake word...")
#             if wake_system.listen():
#                 detected_flag = True
#                 conversation_active = True
#                 _dbg("Wake word -> greeting")
#                 speak_text("Hey Krushna, how can I help you?")

#                 # Close Porcupine mic so we can reuse audio device for STT
#                 try:
#                     if wake_system.audio_stream and wake_system.audio_stream.is_active():
#                         _dbg("Pausing Porcupine mic for STT...")
#                         wake_system.audio_stream.stop_stream()
#                         wake_system.audio_stream.close()
#                         wake_system.audio_stream = None
#                 except Exception as e:
#                     _dbg(f"Error closing Porcupine stream: {e}")

#                 # Conversation loop
#                 while conversation_active and not shutdown_flag:
#                     _dbg("Listening for one user utterance via OpenAI STT...")
#                     user_text = transcribe_once_from_mic(device_index=wake_system.device_index)
#                     _dbg(f"STT -> '{user_text}'")

#                     if not user_text:
#                         _dbg("Empty STT result -> reprompt")
#                         speak_text("Sorry, I didn’t catch that.")
#                         continue

#                     lowered = user_text.lower()
#                     if "goodbye tars" in lowered or "bye tars" in lowered:
#                         _dbg("Goodbye phrase detected -> ending conversation.")
#                         speak_text("Goodbye Krushna, going back to standby.")
#                         conversation_active = False
#                         break

#                     # Brain call
#                     _dbg(f"Brain ask <- '{user_text}'")
#                     reply = ask_brain(user_text)
#                     _dbg(f"Brain reply length={len(reply)}")

#                     # Shorten very long replies for TTS
#                     words = reply.split()
#                     if len(words) > 80:
#                         reply = " ".join(words[:80]) + "..."
#                         _dbg("Reply trimmed to 80 words.")

#                     _dbg("Speaking reply via TTS...")
#                     speak_text(reply)

#                 detected_flag = False
#                 wake_system.reset()
#                 _dbg("Session ended — back to standby.")
#         except Exception as e:
#             print(f"Wakeword loop error: {e}")
#             time.sleep(1)


# # -------------------------------------------------------------
# # Public API for FastAPI router
# # -------------------------------------------------------------
# def start_background_listener():
#     global wake_system, wake_thread, shutdown_flag
#     shutdown_flag = False

#     if not ACCESS_KEY or not KEYWORD_PATH:
#         return {"error": "Missing ACCESS_KEY or KEYWORD_PATH"}

#     if wake_system is None:
#         wake_system = WakeWordSystem(keyword_path=KEYWORD_PATH, access_key=ACCESS_KEY)
#         wake_system.setup()

#     if wake_thread and wake_thread.is_alive():
#         return {"status": "already_listening"}

#     wake_thread = threading.Thread(target=_wakeword_loop, daemon=True)
#     wake_thread.start()
#     return {"status": "listening", "debug": TARS_DEBUG}


# def get_status():
#     return {"detected": detected_flag, "debug": TARS_DEBUG}


# def stop_listener():
#     global shutdown_flag
#     shutdown_flag = True
#     if wake_system:
#         wake_system.cleanup()
#     return {"status": "stopped"}

#******************--------------------***************
"""
wake_word.py
------------
Wake-word listener for TARS.
Pipeline:
- Porcupine wake-word (“Hey TARS”)
- OpenAI Whisper STT
- Brain response (local Phi or OpenAI)
- OpenAI TTS

This updated version ALSO updates:
- voice_state["thinking"]
- voice_state["speaking"]
for frontend hologram animations.
"""

import os
import struct
import threading
import pyaudio
import pvporcupine
from dotenv import load_dotenv

from brain.brain_manager import ask_brain
from voice.text_to_speech_openai import speak_text
from voice.speech_to_text_openai import transcribe_once_from_mic
from routers.vision_routes import set_vision_state


# NEW — shared voice state for SSE endpoint
from routers.dots_routes import voice_state

load_dotenv()

ACCESS_KEY = os.getenv("ACCESS_KEY")
KEYWORD_PATH = os.getenv("KEYWORD_PATH")

DEBUG = os.getenv("TARS_DEBUG", "0").lower() in ("1", "true")


def dbg(msg: str):
    if DEBUG:
        print(f"[DEBUG] {msg}")


# =====================================================================
#                          WAKE-WORD CLASS
# =====================================================================
class WakeWordSystem:
    """Handles Porcupine wake-word detection (“Hey TARS”)."""

    def __init__(self):
        if not ACCESS_KEY or not KEYWORD_PATH:
            raise RuntimeError("Missing Porcupine ACCESS_KEY or KEYWORD_PATH")

        self.porcupine = pvporcupine.create(
            access_key=ACCESS_KEY,
            keyword_paths=[KEYWORD_PATH],
        )

        self.pa = pyaudio.PyAudio()
        self.device_index = self._pick_mic()

        dbg(f"Using input device #{self.device_index}")
        self.stream = self._open()

    # ----------------------------------------------------------------
    def _pick_mic(self):
        """Pick MacBook or iPhone mic automatically."""
        for i in range(self.pa.get_device_count()):
            info = self.pa.get_device_info_by_index(i)
            name = info["name"]
            if "MacBook" in name or "Microphone" in name or "iPhone" in name:
                dbg(f"Selected mic: {name} ({i})")
                return i

        return self.pa.get_default_input_device_info()["index"]

    # ----------------------------------------------------------------
    def _open(self):
        dbg("Opening Porcupine mic…")
        return self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=self.porcupine.frame_length,
        )

    # ----------------------------------------------------------------
    def listen(self):
        """Block until wake-word is detected."""
        dbg("Listening for wakeword…")

        while True:
            pcm = self.stream.read(
                self.porcupine.frame_length,
                exception_on_overflow=False
            )
            frame = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
            result = self.porcupine.process(frame)

            if result >= 0:
                dbg("Wakeword detected!")
                return True


# =====================================================================
#                     MAIN CONVERSATION LOOP (UPDATED)
# =====================================================================
def _loop():
    w = WakeWordSystem()

    while True:
        # ------------------------------------------------------------
        # 1. WAIT FOR WAKE WORD
        # ------------------------------------------------------------
        w.listen()

        # FRONTEND STATE: speaking
        voice_state["speaking"] = True
        voice_state["thinking"] = False

        speak_text("Hey Krushna, how can I help you?")

        # Reset to idle
        voice_state["speaking"] = False
        voice_state["thinking"] = False

        # Close wakeword mic before STT
        w.stream.stop_stream()
        w.stream.close()
        
        # Track if we're waiting for camera choice
        pending_camera_choice = False

        # ------------------------------------------------------------
        # 2. CONVERSATION LOOP
        # ------------------------------------------------------------
        while True:

            dbg("Listening for user speech…")

            # User speaking → audio activity
            voice_state["speaking"] = True
            voice_state["thinking"] = False

            query = transcribe_once_from_mic(device_index=w.device_index)

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

        w.stream = w._open()


# =====================================================================
#                    FASTAPI THREAD INTEGRATION
# =====================================================================
thread = None


def start_background_listener():
    global thread

    if thread and thread.is_alive():
        return {"status": "already_running"}

    thread = threading.Thread(target=_loop, daemon=True)
    thread.start()
    return {"status": "started"}


def get_status():
    return {"status": "running" if thread and thread.is_alive() else "stopped"}


def stop_listener():
    # Actual stop not implemented
    return {"status": "stopping_request_received"}
