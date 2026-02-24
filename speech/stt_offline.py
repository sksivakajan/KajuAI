import os
import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from config import VOSK_MODEL_PATH


_model = None


def get_model():
    global _model
    if _model is None:
        if not os.path.isdir(VOSK_MODEL_PATH):
            raise FileNotFoundError("Vosk model folder not found")
        _model = Model(VOSK_MODEL_PATH)
    return _model


def listen_offline():
    model = get_model()
    rec = KaldiRecognizer(model, 16000)
    q = queue.Queue()

    def callback(indata, frames, time, status):
        q.put(bytes(indata))

    print("Listening (offline)...")

    with sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        for _ in range(50):
            data = q.get()
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                text = res.get("text", "")
                if text:
                    print("You:", text)
                    return text

    return ""