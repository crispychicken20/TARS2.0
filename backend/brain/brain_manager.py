"""
brain_manager.py
----------------
Clean + safe + filtered controller for TARS brain.
Routes between:
    - Local Phi (phi-3.5-mini)
    - Cloud GPT-4o-mini (optional)

Ensures responses are:
    - Short
    - Clean
    - Voice-ready (no markdown, no code blocks, no roles)
"""

import os
import re
from dotenv import load_dotenv

from brain.brain_phi import PhiBrain
from openai import OpenAI

load_dotenv()

USE_CLOUD = os.getenv("USE_CLOUD_LLM", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ---------------------------------------------------------------
# Initialize models
# ---------------------------------------------------------------

# Local fallback model
phi_brain = PhiBrain()

client = None
if USE_CLOUD and OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("[TARS::Brain] Cloud model enabled → GPT-4o-mini active.")
else:
    print("[TARS::Brain] Running on local Phi only.")


# ---------------------------------------------------------------
# Text Cleaner (critical for TTS)
# ---------------------------------------------------------------
def clean_output(text: str) -> str:
    """
    Remove garbage LLM artifacts:
        - Markdown
        - Code blocks
        - Role messages
        - System prompts
        - Alignment text
    Keep only: clean, plain English for voice.
    """

    if not text:
        return ""

    # Remove markdown, bullets, code blocks
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`.*?`", "", text)
    text = re.sub(r"\*\*", "", text)            # bold markers
    text = re.sub(r"[*_#>-]", " ", text)        # markdown characters

    # Remove teacher/role instructions
    text = re.sub(r"(You are|As an AI|System:|Assistant:).*", "", text)

    # Remove "Here is the answer:" or similar boilerplate
    text = re.sub(r"^(Here.*?:|Sure.*?:)", "", text, flags=re.IGNORECASE)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Final safety: truncate long outputs for TTS
    words = text.split()
    if len(words) > 80:
        text = " ".join(words[:80]) + "..."

    return text


# ---------------------------------------------------------------
# Heuristic: When should we call GPT?
# ---------------------------------------------------------------
def is_complex_query(text: str) -> bool:
    """
    GPT is used only when:
      - question is long, OR
      - involves reasoning, coding, explaining, planning.
    """
    triggers = [
        "explain", "analyze", "why", "how",
        "python", "sql", "vision", "image",
        "plan", "code", "mathematics", "reason"
    ]
    long_q = len(text.split()) > 25

    return long_q or any(k in text.lower() for k in triggers)

def summarize(text: str):
    summary_prompt = (
        "Summarize the following answer in 1–2 short spoken sentences, "
        "keeping the meaning but making it concise:\n\n" + text
    )
    result = phi_brain.ask(summary_prompt)
    return clean_output(result)


def trim_sentences(text, max_sentences=2):
    sentences = text.split(".")
    trimmed = ".".join(sentences[:max_sentences]).strip()
    return trimmed + "."



# ---------------------------------------------------------------
# Main Brain Function
# ---------------------------------------------------------------
MAX_CHARS = 160
def ask_brain(query: str) -> str:
    """
    Core function:
    - Takes user query
    - Routes to GPT or Phi
    - Cleans output
    - Returns final TTS-ready text
    """

    # No cloud route → always Phi
    if not USE_CLOUD or not client:
        raw = phi_brain.ask(query)
        return clean_output(raw)

    # Complex -> GPT
    if is_complex_query(query):
        print("[TARS::Brain] Using GPT-4o-mini for reasoning…")

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are TARS, a calm and concise voice assistant. "
                            "Speak in natural conversational English. "
                            "Do not output lists, markdown, formatting, roles, or meta-explanations. "
                            "Respond as if you are talking directly to Krushna."
                        ),
                    },
                    {"role": "user", "content": query},
                ]
            )

            raw = response.choices[0].message.content
            cleaned = clean_output(raw)
            
            if len(cleaned) > MAX_CHARS:
                cleaned = summarize(cleaned)

            cleaned = trim_sentences(cleaned, max_sentences=2)
            
            print("[TARS::Brain] GPT output:", cleaned)
            return cleaned

        except Exception as e:
            print("[TARS::Brain] GPT error → falling back to Phi:", e)

    # Default → Phi local brain
    raw = phi_brain.ask(query)
    cleaned = clean_output(raw)

    print("[TARS::Brain] Phi output:", cleaned)
    return cleaned
