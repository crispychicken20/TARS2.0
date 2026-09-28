"""
brain_phi.py
------------
Local conversational brain using Phi-3.5-mini (via Ollama).
Optimized for TARS voice interactions:
    - Short, natural speech responses
    - No markdown, no lists, no formatting
    - No hallucinated personas
    - Memory-conscious dialogue
"""

import requests
import re
from datetime import datetime
from typing import List, Dict

OLLAMA_URL = "http://localhost:11434/api/generate"


class PhiBrain:
    def __init__(self, model: str = "phi3:mini", memory_limit: int = 10):
        self.model = model
        self.chat_history: List[Dict[str, str]] = []
        self.memory_limit = memory_limit

    # --------------------------------------------------------------
    # SYSTEM PROMPT — Foundation of TARS behavior
    # --------------------------------------------------------------
    def system_prompt(self) -> str:
        return (
            "You are TARS, a calm, intelligent voice assistant built by Krushna. "
            "Speak in clear, conversational English. "
            "Keep responses short (1–3 sentences). "
            "Never give long explanations unless explicitly asked"
            "Never use markdown, never list items, never show bullets, "
            "never output code or formatting. "
            "Do not describe yourself as a model. "
            "Do not invent personas like TRANSISTOR. "
            "Respond exactly like you're speaking to a human."
        )

    # --------------------------------------------------------------
    # CLEANING — Absolutely required for TTS safety
    # --------------------------------------------------------------
    def _clean_response(self, text: str) -> str:
        if not text:
            return ""

        # Remove code blocks, markdown, symbols
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        text = re.sub(r"`.*?`", "", text)
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        text = re.sub(r"#{1,6}\s*", "", text)
        text = re.sub(r"[*_•>\-]+", " ", text)

        # Remove system or persona hallucinations
        text = re.sub(r"^(You are|As an AI|System:|Assistant:).*", "", text, flags=re.IGNORECASE)

        # Remove instructions / meta text
        text = re.sub(r"(Instruction:|Task:|Analysis:).*", "", text, flags=re.DOTALL)

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()

        # Limit to max 3 spoken sentences
        sentences = re.split(r"(?<=[.!?])\s+", text)
        text = " ".join(sentences[:3]).strip()

        # Limit runaway word count (80 words max)
        words = text.split()
        if len(words) > 80:
            text = " ".join(words[:80]) + "..."

        return text

    # --------------------------------------------------------------
    # MEMORY TRIM
    # --------------------------------------------------------------
    def _truncate_memory(self):
        if len(self.chat_history) > self.memory_limit:
            self.chat_history = self.chat_history[-self.memory_limit:]

    # --------------------------------------------------------------
    # LOCAL OLLAMA CALL — Phi-3.5-mini
    # --------------------------------------------------------------
    def _call_ollama(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        try:
            res = requests.post(OLLAMA_URL, json=payload, timeout=120)
            res.raise_for_status()
            return res.json().get("response", "").strip()

        except Exception as e:
            print("[PhiBrain] Ollama error:", e)
            return "Sorry, my local processor is unavailable right now."

    # --------------------------------------------------------------
    # MAIN ENTRY — Ask Phi-mini
    # --------------------------------------------------------------
    def ask(self, user_query: str) -> str:
        timestamp = datetime.now().strftime("%H:%M")

        # Store user message
        self.chat_history.append({
            "role": "user",
            "content": user_query,
            "time": timestamp
        })
        self._truncate_memory()

        # Build model prompt
        prompt = self.system_prompt() + "\n\n"

        for msg in self.chat_history:
            role = "User" if msg["role"] == "user" else "TARS"
            prompt += f"{role}: {msg['content']}\n"

        prompt += "TARS:"

        # Query local model
        raw = self._call_ollama(prompt)
        cleaned = self._clean_response(raw)

        # Save assistant reply
        self.chat_history.append({
            "role": "assistant",
            "content": cleaned,
            "time": timestamp
        })
        self._truncate_memory()

        print(f"[PhiBrain] TARS:", cleaned)
        return cleaned

    # --------------------------------------------------------------
    def reset(self):
        self.chat_history = []
        print("[PhiBrain] Memory cleared.")
