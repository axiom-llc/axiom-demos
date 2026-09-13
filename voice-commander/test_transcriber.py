import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import numpy as np

import transcriber


class TestLiveTranscriber(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

        self.model_path = Path(self.tmp.name) / "model"
        self.model_path.mkdir()

        self.settings = {
            "model_path": str(self.model_path),
            "target_sample_rate": 16000,
            "device_id": None,
            "buffer_size": 4,
        }

    def _make_transcriber(self):
        with patch("transcriber.Model") as model_cls:
            live = transcriber.LiveTranscriber(self.settings)
            model_cls.assert_called_once_with(str(self.model_path))
        return live

    def test_audio_callback_queues_exact_bytes(self):
        live = self._make_transcriber()

        payload = b"\x01\x00\x02\x00"
        live._audio_callback(payload, frames=2, time=None, status=None)

        self.assertEqual(live.audio_queue.get_nowait(), payload)

    def test_stream_feeds_audio_across_partial_recognition(self):
        live = self._make_transcriber()

        first = b"\x01\x00\x02\x00"
        second = b"\x03\x00\x04\x00"
        live.audio_queue.put(first)
        live.audio_queue.put(second)

        stream = SimpleNamespace(samplerate=48000)
        stream_cm = MagicMock()
        stream_cm.__enter__.return_value = stream
        stream_cm.__exit__.return_value = False

        recognizer = MagicMock()
        recognizer.AcceptWaveform.side_effect = [False, True]
        recognizer.Result.return_value = json.dumps({"text": "hello world"})

        def identity_resample(audio, source_rate, target_rate):
            self.assertEqual(source_rate, 48000)
            self.assertEqual(target_rate, 16000)
            return audio.astype(np.float64)

        with (
            patch("transcriber.sd.RawInputStream", return_value=stream_cm) as raw_stream,
            patch("transcriber.KaldiRecognizer", return_value=recognizer) as recognizer_cls,
            patch("transcriber.resampy.resample", side_effect=identity_resample) as resample,
        ):
            generator = live.start_stream()
            try:
                self.assertEqual(next(generator), "hello world")
            finally:
                generator.close()

        raw_stream.assert_called_once_with(
            device=None,
            dtype="int16",
            channels=1,
            callback=live._audio_callback,
        )
        recognizer_cls.assert_called_once_with(live.model, 16000)
        self.assertEqual(resample.call_count, 2)
        self.assertEqual(recognizer.AcceptWaveform.call_count, 2)
        self.assertEqual(
            [call.args[0] for call in recognizer.AcceptWaveform.call_args_list],
            [first, second],
        )
        recognizer.Result.assert_called_once_with()
        stream_cm.__exit__.assert_called_once()


if __name__ == "__main__":
    unittest.main()
