"""
TARS Vision Module (Tiny Model - Real Time)
-------------------------------------------
Uses a lightweight ViT-GPT2 model (~145MB).
Fast. No heavy downloads. Works with 3GB free space.

Model: nlpconnect/vit-gpt2-image-captioning
"""

import re
import torch
from PIL import Image
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer

MODEL_ID = "nlpconnect/vit-gpt2-image-captioning"

_model = None
_processor = None
_tokenizer = None


def _load_model():
    global _model, _processor, _tokenizer

    if _model is not None:
        return

    print("[TARS::Vision] Loading tiny captioning model…")

    device = "mps" if torch.backends.mps.is_available() else "cpu"

    _model = VisionEncoderDecoderModel.from_pretrained(MODEL_ID).to(device)
    _processor = ViTImageProcessor.from_pretrained(MODEL_ID)
    _tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

    _model.eval()
    print(f"[TARS::Vision] Loaded on device: {device}")


def _clean(text: str) -> str:
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"[`*#{}\\_]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if "." in text:
        return text.split(".")[0] + "."
    return text


def analyze_image(image_path: str, question="Describe this image."):
    _load_model()

    img = Image.open(image_path).convert("RGB")
    pixel_values = _processor(images=img, return_tensors="pt").pixel_values.to(_model.device)

    with torch.no_grad():
        output_ids = _model.generate(pixel_values, max_length=50)

    caption = _tokenizer.decode(output_ids[0], skip_special_tokens=True)
    cleaned = _clean(caption)

    print("[TARS::Vision] Output:", cleaned)
    return cleaned
