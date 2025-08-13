"""Speech-to-text utilities using :mod:`faster_whisper`."""
from __future__ import annotations

from functools import lru_cache

from faster_whisper import WhisperModel


@lru_cache(maxsize=2)
def _get_model(model_size: str) -> WhisperModel:
    return WhisperModel(model_size, device="cuda", compute_type="float16")


def transcribe(wav_path: str, model_size: str = "medium.en") -> str:
    """Transcribe ``wav_path`` and return the recognised text."""
    model = _get_model(model_size)
    segments, _info = model.transcribe(wav_path)
    return " ".join(seg.text.strip() for seg in segments)
