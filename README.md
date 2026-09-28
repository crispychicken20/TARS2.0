# 🤖 TARS: Voice-Activated AI Assistant
Testing pattern

TARS is a modular, intelligent assistant system designed to emulate a personalized AI experience — starting with a simple wake word and growing into a full conversational assistant.

---

## 🛠️ Project Setup

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/tars-ai-assistant.git
cd tars-ai-assistant

# 2. Setup virtual environment (recommended)
conda create -n tars python=3.11
conda activate tars

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run device check (optional)
python list_devices.py

# 5. Run the assistant
python main.py
```

---

## ✅ Current Progress

### ✅ Step 1: Wake Word Detection (Complete)
- Using Picovoice Porcupine with custom `Hey TARS` model.
- Microphone streaming via PyAudio.
- Wake word triggers the assistant pipeline.
- Keyword model: `models/HEY-TARS_en_mac_v3_0_0.ppn`

### ✅ Step 2: Speech-to-Text (STT)
- Implemented with **Vosk Offline STT**
- Converts live microphone input to text after wake-word detection

---

### ✅ Step 3: Text-to-Speech (TTS)
- Implemented using **pyttsx3**
- Converts assistant’s response into natural voice output

---

### ✅ Step 4: Voice Assistance Pipeline
- End-to-end voice loop working: Wake Word → STT → Brain → TTS  
- Real-time response with seamless audio feedback

---

### ✅ Step 5: Brain Module
- Core logic handled by `brain/brain.py` and `brain/personality.py`  
- Processes commands, routes to sub-modules, and generates replies  
- Includes lightweight rule-based + LLM expansion support

---

### ✅ Step 6: Frontend UI
- React-based interface under `FRONTEND/tars`  
- Includes navigation, about page, and design modules  
- Acts as visual dashboard for user interactions

---

### ✅ Step 7: Weather Utility
- Located in `Utils/weather/`  
- Fetches live weather data and verbalizes results through TTS

---

### ✅ Step 8: Camera Utility
- Located in `Utils/camera/`  
- Captures image/video input for future computer-vision integration

---

### 🔄 Step 9: Integration Phase (In Progress)
- Connecting **Brain + Voice + UI + Weather + Camera** for unified behavior  
- Enables full multimodal assistant experience with live visual feedback

---

---


## 🧭 Roadmap

### 🔄 Step 2: Speech-to-Text
- Use Whisper / Google STT API
- Transcribe user command after wake word

### 🧠 Step 3: Brain Module
- Route text to `brain/personality.py`
- Generate responses (rule-based or LLM-powered)

### 🎙️ Step 4: Text-to-Speech
- Output audio response using pyttsx3 / ElevenLabs

### 🌐 Step 5: Web Search Module (optional)
- Add real-time web retrieval via DuckDuckGo / SerpAPI

### 💬 Step 6: Chat History / Memory
- Maintain context over conversations

---

## 🗂️ Folder Structure

```
TARS/
├── main.py                      # Entry point for complete assistant pipeline
├── list_devices.py              # Tool to inspect microphone devices
├── requirements.txt
├── .env                         # Environment variables (ACCESS_KEY, etc.)
│
├── brain/                       # Core logic and personality
│   ├── brain.py
│   └── personality.py
│
├── voice/                       # Voice I/O modules
│   ├── speech_to_text.py
│   └── text_to_speech.py
│
├── wake_word/                   # Wake-word detection (Picovoice Porcupine)
│   └── wake_word.py
│
├── models/                      # Wake-word model files (.ppn)
│   └── HEY-TARS_en_mac_v3_0_0.ppn
│
├── Utils/                       # Additional assistant utilities
│   ├── weather/                 # Weather API & response handler
│   ├── camera/                  # Camera capture and processing
│   └── movie/                   # (Future) Movie recommendations / info
│
├── FRONTEND/                    # React web interface for TARS
│   └── tars/
│       ├── public/
│       └── src/
│           ├── App.js
│           ├── Navigation.js
│           ├── Design/
│           ├── About.js
│           └── index.js
│
└── README.md

```

---

## 👨‍💻 Author

**Krushna Thakkar**  
AI Researcher | MSAI @ SJSU | Hobbyist Builder  
[GitHub](https://github.com/kru2710shna) • [Website](https://localhost0027.netlify.app)

---

## 📜 License

MIT License. See `LICENSE` file.
