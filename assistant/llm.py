"""Interface to a local Ollama large language model."""
from __future__ import annotations

import json
import requests

OLLAMA_URL = "http://localhost:11434"


def _route_tool(block: dict) -> str:
    """Delegate tool invocation to :mod:`intents`."""
    from . import intents

    return intents.handle_tool(block)


def chat(prompt: str, system: str | None = None) -> str:
    """Send ``prompt`` to the LLM and return its textual response.

    If the model returns a JSON object with ``tool`` and ``args`` fields
    it is interpreted as a function call and routed to
    :func:`intents.handle_tool`.
    """

    payload: dict[str, object] = {"model": "llama3.1", "prompt": prompt}
    if system:
        payload["system"] = system
    resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
    resp.raise_for_status()
    text = resp.json().get("response", "")
    try:
        block = json.loads(text)
    except json.JSONDecodeError:
        return text
    if isinstance(block, dict) and "tool" in block:
        return _route_tool(block)
    return text
