"""Offline speech-to-text skill using Vosk."""
from __future__ import annotations
import os
from typing import Optional

import wave
from vosk import Model, KaldiRecognizer

VOICE_MODEL_PATH = os.getenv("VOICE_MODEL_PATH", "models/vosk")

class VoiceInput:
    """Transcribe audio files or microphone input using Vosk."""

    ROLE = "skill"

    def __init__(self, model_path: str | None = None):
        self.model_path = model_path or VOICE_MODEL_PATH
        self.model: Optional[Model] = None

    def load(self):
        if self.model is None:
            self.model = Model(self.model_path)

    def transcribe_file(self, path: str) -> str:
        self.load()
        wf = wave.open(path, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in (8000, 16000, 44100):
            raise ValueError("Unsupported audio format")
        rec = KaldiRecognizer(self.model, wf.getframerate())
        result = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                res = rec.Result()
                result.append(res)
        final = rec.FinalResult()
        result.append(final)
        return " ".join(result)
