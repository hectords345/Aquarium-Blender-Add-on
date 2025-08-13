from __future__ import annotations

import numpy as np
import sounddevice as sd

from assistant import audio_io


def test_record_play(monkeypatch, tmp_path):
    frames = []

    def fake_rec(n_frames, samplerate, channels):
        frames.append(n_frames)
        return np.zeros((n_frames, channels), dtype=np.float32)

    def fake_play(data, rate):
        assert data.size > 0

    monkeypatch.setattr(sd, "rec", fake_rec)
    monkeypatch.setattr(sd, "play", fake_play)
    monkeypatch.setattr(sd, "wait", lambda: None)

    path = audio_io.record_seconds(0.1, samplerate=8000)
    assert frames[0] == 800
    audio_io.play_wav(path)
