import json
import tempfile
import unittest
from pathlib import Path

import config


class TestLoadConfigValidation(unittest.TestCase):
    def _write_config(self, data):
        root = tempfile.TemporaryDirectory()
        path = Path(root.name) / "config.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        self.addCleanup(root.cleanup)
        return path

    def test_missing_settings_raises_value_error(self):
        path = self._write_config({"commands": {"dynamic": {}}})
        with self.assertRaisesRegex(
            ValueError,
            "Config file is missing 'settings' or 'commands' section.",
        ):
            config.load_config(path)

    def _valid_config(self):
        return {
            "settings": {
                "model_path": "~/model",
                "target_sample_rate": 16000,
                "device_id": None,
                "buffer_size": 4096,
            },
            "commands": {"static": {}},
        }

    def test_missing_required_setting_raises_value_error(self):
        for key in ("model_path", "target_sample_rate", "device_id", "buffer_size"):
            with self.subTest(key=key):
                data = self._valid_config()
                del data["settings"][key]
                path = self._write_config(data)
                with self.assertRaisesRegex(ValueError, key):
                    config.load_config(path)

    def test_invalid_sample_rate_rejected(self):
        data = self._valid_config()
        data["settings"]["target_sample_rate"] = 0
        path = self._write_config(data)
        with self.assertRaisesRegex(ValueError, "target_sample_rate"):
            config.load_config(path)

    def test_invalid_buffer_size_rejected(self):
        data = self._valid_config()
        data["settings"]["buffer_size"] = 0
        path = self._write_config(data)
        with self.assertRaisesRegex(ValueError, "buffer_size"):
            config.load_config(path)

    def test_null_device_id_is_allowed(self):
        path = self._write_config(self._valid_config())
        cfg = config.load_config(path)
        self.assertIsNone(cfg["settings"]["device_id"])

    def test_missing_dynamic_section_is_allowed(self):
        data = self._valid_config()
        data["commands"] = {"static": {}}
        path = self._write_config(data)
        cfg = config.load_config(path)
        self.assertEqual(cfg["commands"], {"static": {}})

    def test_missing_commands_raises_value_error(self):
        path = self._write_config({"settings": {"model_path": "~/model"}})
        with self.assertRaisesRegex(
            ValueError,
            "Config file is missing 'settings' or 'commands' section.",
        ):
            config.load_config(path)

    def test_argv_commands_require_nonempty_string_arrays(self):
        data=self._valid_config(); data["commands"]["argv"]={"director health":["python","wrapper.py","health"]}
        self.assertEqual(config.load_config(self._write_config(data))["commands"]["argv"]["director health"][0],"python")
        data=self._valid_config(); data["commands"]["argv"]={"bad":"shell string"}
        with self.assertRaisesRegex(ValueError,"argv"):
            config.load_config(self._write_config(data))


if __name__ == "__main__":
    unittest.main()
