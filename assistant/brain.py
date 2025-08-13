"""Main orchestration logic tying all components together."""
from __future__ import annotations

import logging

from . import audio_io, intents, stt, tts, wake

logger = logging.getLogger(__name__)

last_transcript: str | None = None
last_response: str | None = None


class Brain:
    """Runs the assistant interaction loop."""

    def __init__(self, stt_model: str = "medium.en") -> None:
        self.stt_model = stt_model

    def run_once(self) -> None:
        global last_transcript, last_response
        wake.listen_for_wake()
        wav = audio_io.record_seconds()
        logger.info("recorded audio at %s", wav)
        last_transcript = stt.transcribe(wav, self.stt_model)
        logger.info("transcript: %s", last_transcript)
        last_response = intents.handle_command(last_transcript)
        logger.info("response: %s", last_response)
        tts.speak(last_response)

    def run(self) -> None:
        while True:
            try:
                self.run_once()
            except Exception as exc:  # pragma: no cover - safety net
                logger.exception("Error in interaction loop: %s", exc)
                try:
                    tts.speak("Sorry, something went wrong")
                except Exception:
                    pass
