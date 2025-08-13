"""Helpers for interacting with the Scrypted REST API."""
from __future__ import annotations

import requests

from . import config


def _headers() -> dict[str, str]:
    if not config.SCRYPTED_TOKEN:
        raise RuntimeError("SCRYPTED_TOKEN is not configured")
    return {"Authorization": f"Bearer {config.SCRYPTED_TOKEN}"}


def list_devices() -> list[dict]:
    resp = requests.get(f"{config.SCRYPTED_URL}/api/devices", headers=_headers())
    resp.raise_for_status()
    return resp.json()


def snapshot(device_id: str) -> bytes:
    resp = requests.get(
        f"{config.SCRYPTED_URL}/api/devices/{device_id}/snapshot",
        headers=_headers(),
    )
    resp.raise_for_status()
    return resp.content


def arm(device_id: str) -> bool:
    """Attempt to arm the specified device.

    Some devices may not support this feature.  The function returns
    ``False`` if the endpoint is not found (HTTP 404).
    """

    url = f"{config.SCRYPTED_URL}/api/devices/{device_id}/arm"
    resp = requests.post(url, headers=_headers())
    if resp.status_code == 404:
        return False
    resp.raise_for_status()
    return True
