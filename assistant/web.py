"""FastAPI application exposing simple health/status endpoints."""
from __future__ import annotations

import subprocess
from typing import Any

from fastapi import FastAPI

from . import brain, tts

app = FastAPI()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/status")
async def status() -> dict[str, Any]:
    """Return last transcript/response and GPU memory usage if available."""
    try:
        mem = (
            subprocess.check_output(
                [
                    "nvidia-smi",
                    "--query-gpu=memory.used",
                    "--format=csv,noheader,nounits",
                ]
            )
            .decode()
            .strip()
        )
    except Exception:
        mem = "unknown"
    return {
        "last_transcript": brain.last_transcript,
        "last_response": brain.last_response,
        "gpu_mem": mem,
    }


@app.post("/say")
async def say(text: str) -> dict[str, str]:
    tts.speak(text)
    return {"status": "ok"}


@app.get("/")
async def index() -> str:
    return (
        "<html><body><h1>Assistant</h1>"
        f"<p>Last transcript: {brain.last_transcript}</p>"
        f"<p>Last response: {brain.last_response}</p>"
        "</body></html>"
    )
