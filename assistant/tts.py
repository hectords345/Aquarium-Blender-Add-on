"""Text-to-speech helpers."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from . import audio_io


def _run_cmd(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def speak(text: str) -> Path:
    """Speak ``text`` using an available CLI TTS engine.

    The generated audio is written to ``reply.wav`` in the current
    working directory and then played back.  The path is returned.
    """

    out = Path("reply.wav")
    if shutil.which("tts"):
        _run_cmd(["tts", "--text", text, "--out_path", str(out)])
    elif shutil.which("piper"):
        _run_cmd(["piper", "--text", text, "--output_file", str(out)])
    else:  # pragma: no cover - depends on external software
        raise RuntimeError("No TTS engine available")
    audio_io.play_wav(str(out))
    return out
