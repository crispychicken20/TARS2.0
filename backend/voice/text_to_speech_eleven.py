# """
# text_to_speech_eleven.py
# ElevenLabs TTS for TARS
# """

# import os
# from elevenlabs import ElevenLabs
# from dotenv import load_dotenv

# load_dotenv()
# API = os.getenv("ELEVENLABS_API_KEY")
# if not API:
#     raise RuntimeError("ELEVENLABS_API_KEY missing")

# client = ElevenLabs(api_key=API)
# VOICE = "EXAVITQu4vr4xnSDxMaL"


# def speak_text(text: str):
#     try:
#         print("TARS:", text)
#         audio = client.text_to_speech.convert(
#             voice_id=VOICE,
#             model_id="eleven_multilingual_v2",
#             text=text,
#         )

#         os.makedirs("tmp_audio", exist_ok=True)
#         path = "tmp_audio/output.mp3"
#         with open(path, "wb") as f:
#             for chunk in audio:
#                 if chunk:
#                     f.write(chunk)

#         os.system(f"afplay {path}")
#     except Exception as e:
#         print("TTS ERROR:", e)
