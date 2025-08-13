"""Simple intent routing for natural language commands."""
from __future__ import annotations

import re

from . import config, llm, scrypted, vlm


def _resolve(room: str) -> str | None:
    return config.DEVICE_IDS.get(room.lower())


def handle_command(text: str) -> str:
    """Route ``text`` to the appropriate handler."""
    text_low = text.lower()
    m = re.search(r"describe (.+?) camera", text_low)
    if m:
        room = m.group(1).strip()
        device_id = _resolve(room)
        if not device_id:
            return f"Unknown device for {room}"
        image = scrypted.snapshot(device_id)
        return vlm.analyze_image(f"Describe the {room} camera", image)

    m = re.search(r"arm (.+?) camera", text_low)
    if m:
        room = m.group(1).strip()
        device_id = _resolve(room)
        if not device_id:
            return f"Unknown device for {room}"
        return "Armed" if scrypted.arm(device_id) else "Unable to arm"

    return llm.chat(text)


def handle_tool(block: dict) -> str:
    """Handle JSON tool calls emitted by the LLM."""
    tool = block.get("tool")
    args = block.get("args", {})
    if tool == "scrypted.snapshot":
        device_id = args.get("device_id")
        if not device_id:
            return "device_id missing"
        image = scrypted.snapshot(device_id)
        prompt = args.get("prompt", "Describe the snapshot")
        return vlm.analyze_image(prompt, image)
    if tool == "scrypted.arm":
        device_id = args.get("device_id")
        if not device_id:
            return "device_id missing"
        return "Armed" if scrypted.arm(device_id) else "Unable to arm"
    return "Unknown tool"
