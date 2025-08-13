"""Wake-word and push-to-talk handling."""
from __future__ import annotations

import time
import keyboard

from . import audio_io, config

try:  # openwakeword may not be installed on all systems
    import openwakeword
except Exception:  # pragma: no cover - only triggered when lib missing
    openwakeword = None


_LAST_TRIGGER = 0.0


def listen_for_wake(threshold: float = 0.75) -> str:
    """Block until the wake word or push-to-talk key is detected.

    Returns ``"wakeword"`` or ``"push_to_talk"`` depending on what fired.
    A simple debounce prevents rapid re-triggering.
    """

    global _LAST_TRIGGER

    if config.USE_PUSH_TO_TALK:
        keyboard.wait(config.PTT_KEY)
        _LAST_TRIGGER = time.time()
        return "push_to_talk"

    if openwakeword is None:
        raise RuntimeError("openwakeword not available")

    model = openwakeword.Model(wakewords=[config.WAKEWORD])
    stream, q = audio_io.microphone_stream()

    try:
        while True:
            data = q.get()
            scores = model.predict(data)
            score = scores.get(config.WAKEWORD, 0.0)
            now = time.time()
            if score > threshold and now - _LAST_TRIGGER > 1.0:
                _LAST_TRIGGER = now
                return "wakeword"
            if keyboard.is_pressed(config.PTT_KEY) and now - _LAST_TRIGGER > 1.0:
                _LAST_TRIGGER = now
                return "push_to_talk"
    finally:
        stream.stop()
        stream.close()
