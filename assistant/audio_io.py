"""Audio input/output utilities using :mod:`sounddevice`.

The module exposes a non-blocking microphone stream and convenience
functions for recording audio to a temporary WAV file and playing WAV
files.
"""
from __future__ import annotations

import queue
import tempfile
import wave
from pathlib import Path
from typing import Generator

import numpy as np
import sounddevice as sd

# ---------------------------------------------------------------------------
# Streaming microphone input


def microphone_stream(
    samplerate: int = 16_000, channels: int = 1
) -> tuple[sd.InputStream, "queue.Queue[np.ndarray]"]:
    """Return a started :class:`~sounddevice.InputStream` and a queue.

    Audio chunks are put into the queue as numpy arrays.  The caller is
    responsible for stopping and closing the stream.
    """

    q: "queue.Queue[np.ndarray]" = queue.Queue()

    def _callback(indata, frames, time, status):
        if status:
            print("InputStream status:", status)
        q.put(indata.copy())

    stream = sd.InputStream(
        samplerate=samplerate, channels=channels, callback=_callback
    )
    stream.start()
    return stream, q


# ---------------------------------------------------------------------------
# Convenience helpers


def record_seconds(
    seconds: float = 4.0, samplerate: int = 16_000, channels: int = 1
) -> str:
    """Record audio for ``seconds`` and return path to a temporary WAV file."""
    frames = int(seconds * samplerate)
    data = sd.rec(frames, samplerate=samplerate, channels=channels)
    sd.wait()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        path = Path(f.name)

    # Write WAV file using 16‑bit PCM
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(samplerate)
        wf.writeframes((data * 32767).astype(np.int16).tobytes())
    return str(path)


def play_wav(path: str) -> None:
    """Play a WAV file located at ``path``."""
    with wave.open(path, "rb") as wf:
        data = wf.readframes(wf.getnframes())
        sd.play(np.frombuffer(data, dtype=np.int16), wf.getframerate())
        sd.wait()
