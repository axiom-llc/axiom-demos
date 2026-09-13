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

    def test_missing_commands_raises_value_error(self):
        path = self._write_config({"settings": {"model_path": "~/model"}})
        with self.assertRaisesRegex(
            ValueError,
            "Config file is missing 'settings' or 'commands' section.",
        ):
            config.load_config(path)


if __name__ == "__main__":
    unittest.main()
