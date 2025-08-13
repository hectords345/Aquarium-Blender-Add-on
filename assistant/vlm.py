"""Vision-language model helpers using Ollama's ``llava`` model."""
from __future__ import annotations

import base64
import requests

from .llm import OLLAMA_URL


def analyze_image(prompt: str, image_bytes: bytes) -> str:
    """Return a short description and safety summary for ``image_bytes``."""
    b64 = base64.b64encode(image_bytes).decode("ascii")
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image", "image": b64},
            ],
        }
    ]
    payload = {"model": "llava", "messages": messages}
    resp = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json().get("message", {}).get("content", "")
