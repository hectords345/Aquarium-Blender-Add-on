"""Configuration handling for the assistant.

Loads environment variables from a ``.env`` file using
:mod:`python-dotenv`.
"""
from __future__ import annotations

import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# --- Required configuration -------------------------------------------------
SCRYPTED_URL: str | None = os.getenv("SCRYPTED_URL")
SCRYPTED_TOKEN: str | None = os.getenv("SCRYPTED_TOKEN")

# --- Optional configuration -------------------------------------------------
WAKEWORD: str = os.getenv("WAKEWORD", "hey_nova")
VOICE: str = os.getenv("VOICE", "en_US")

# Device ID mapping used by :mod:`intents` to resolve rooms to cameras.
# Users should edit their ``.env`` or modify this dictionary at runtime.
DEVICE_IDS: dict[str, str] = {}

# Flags controlling push-to-talk behaviour
USE_PUSH_TO_TALK: bool = os.getenv("USE_PUSH_TO_TALK", "false").lower() in {
    "1", "true", "yes"
}
PTT_KEY: str = os.getenv("PTT_KEY", "F9")
