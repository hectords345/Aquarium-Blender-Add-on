from __future__ import annotations

import requests

from assistant import scrypted


def test_headers_and_urls(monkeypatch):
    scrypted.config.SCRYPTED_URL = "http://host"
    scrypted.config.SCRYPTED_TOKEN = "token"

    calls = []

    class Resp:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"ok": True}

        @property
        def content(self):
            return b"data"

    def fake_get(url, headers):
        calls.append((url, headers))
        return Resp()

    def fake_post(url, headers):
        calls.append((url, headers))
        return Resp()

    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(requests, "post", fake_post)

    scrypted.list_devices()
    scrypted.snapshot("dev")
    scrypted.arm("dev")

    assert calls[0][0] == "http://host/api/devices"
    for _url, headers in calls:
        assert headers["Authorization"] == "Bearer token"
