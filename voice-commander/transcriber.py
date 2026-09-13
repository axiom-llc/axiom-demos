# voice-commander/transcriber.py
"""Encapsulates all audio processing and speech-to-text logic."""
import queue
import json
import sys
from pathlib import Path

import numpy as np
import resampy
import sounddevice as sd
from vosk import KaldiRecognizer, Model


class LiveTranscriber:
    def __init__(self, settings: dict):
        self.settings = settings
        self.audio_queue = queue.Queue()

        model_path = Path(self.settings["model_path"])
        if not model_path.exists():
            raise FileNotFoundError(f"Vosk model not found at: {model_path}")

        print("Loading model...", file=sys.stderr)
        self.model = Model(str(model_path))
        print("Model loaded successfully.", file=sys.stderr)

    def _audio_callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        self.audio_queue.put(bytes(indata))

    def start_stream(self):
        """A generator that yields transcribed text from the microphone."""
        with sd.RawInputStream(
            device=self.settings["device_id"],
            dtype='int16',
            channels=1,
            callback=self._audio_callback
        ) as stream:
            device_samplerate = stream.samplerate
            print(f"Mic Initialized at {int(device_samplerate)} Hz. Listening...", file=sys.stderr)

            recognizer = KaldiRecognizer(self.model, self.settings["target_sample_rate"])
            processing_buffer = b''

            while True:
                processing_buffer += self.audio_queue.get()
                if len(processing_buffer) < self.settings["buffer_size"]:
                    continue

                audio_np = np.frombuffer(processing_buffer, dtype=np.int16)
                resampled_audio = resampy.resample(
                    audio_np, device_samplerate, self.settings["target_sample_rate"]
                )
                resampled_data = resampled_audio.astype(np.int16).tobytes()

                if recognizer.AcceptWaveform(resampled_data):
                    result = json.loads(recognizer.Result())
                    if result.get('text'):
                        yield result['text']

                processing_buffer = b''
