from __future__ import annotations

import base64
import json

import requests

from assistant import llm, vlm


def test_llm_request(monkeypatch):
    sent = {}

    class Resp:
        def __init__(self, data):
            self._data = data

        def raise_for_status(self):
            pass

        def json(self):
            return self._data

    def fake_post(url, json=None, timeout=0):  # noqa: A003 - shadow builtin
        sent["url"] = url
        sent["json"] = json
        return Resp({"response": "hello"})

    monkeypatch.setattr(requests, "post", fake_post)
    out = llm.chat("hi")
    assert out == "hello"
    assert sent["url"].endswith("/api/generate")
    assert sent["json"]["model"] == "llama3.1"


def test_vlm_request(monkeypatch):
    sent = {}

    class Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"message": {"content": "ok"}}

    def fake_post(url, json=None, timeout=0):  # noqa: A003
        sent["url"] = url
        sent["json"] = json
        return Resp()

    monkeypatch.setattr(requests, "post", fake_post)
    result = vlm.analyze_image("prompt", b"bytes")
    assert result == "ok"
    assert sent["url"].endswith("/api/chat")
    assert sent["json"]["model"] == "llava"
    img_b64 = sent["json"]["messages"][0]["content"][1]["image"]
    assert base64.b64decode(img_b64) == b"bytes"
