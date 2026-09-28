# """
# speech_to_text_whisper.py
# -------------------------
# Local transcription using OpenAI Whisper (auto-detects the best microphone).
# """

# import os
# import pyaudio
# import sounddevice as sd
# import soundfile as sf
# import tempfile
# import torch
# import whisper

# MODEL_NAME = "small"  # balanced accuracy and speed
# SAMPLE_RATE = 16000


# def detect_input_device():
#     """Auto-detect and select the most appropriate microphone device."""
#     pa = pyaudio.PyAudio()
#     selected_index = None
#     best_match = None

#     print("Scanning for microphone devices...")
#     for i in range(pa.get_device_count()):
#         info = pa.get_device_info_by_index(i)
#         name = info["name"]
#         channels = info.get("maxInputChannels", 0)

#         if channels > 0:
#             print(f"[{i}] {name} ({channels} channels)")
#             if "MacBook Pro Microphone" in name or "Microphone" in name or "External" in name:
#                 selected_index = i
#                 best_match = name
#                 break

#     if selected_index is None:
#         selected_index = pa.get_default_input_device_info()["index"]
#         best_match = pa.get_default_input_device_info()["name"]

#     pa.terminate()
#     print(f"Selected input device: [{selected_index}] {best_match}")
#     return selected_index


# def record_audio(duration=5, sample_rate=SAMPLE_RATE):
#     """Record raw audio from the selected microphone."""
#     device_index = detect_input_device()
#     print(f"Recording for {duration} seconds on device #{device_index}...")
#     audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, device=device_index)
#     sd.wait()
#     temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
#     sf.write(temp_file.name, audio, sample_rate)
#     print(f"Saved temporary audio: {temp_file.name}")
#     return temp_file.name


# def transcribe_audio(file_path):
#     """Transcribe the given audio file using Whisper."""
#     print(f"Loading Whisper model: {MODEL_NAME}")
#     device = "cuda" if torch.cuda.is_available() else "cpu"
#     model = whisper.load_model(MODEL_NAME, device=device)
#     result = model.transcribe(file_path)
#     print(f"Transcription result: {result['text']}")
#     return result["text"].strip()


# def record_and_transcribe(duration=5):
#     """Complete STT pipeline: record microphone input → transcribe → return text."""
#     file_path = record_audio(duration)
#     try:
#         text = transcribe_audio(file_path)
#     finally:
#         os.remove(file_path)
#     return text


# if __name__ == "__main__":
#     transcription = record_and_transcribe(5)
#     print(f"Final Transcription: {transcription}")
