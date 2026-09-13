# voice-commander/config.py
"""Handles loading and validating the JSON configuration file."""
import json
from pathlib import Path
from typing import Dict, Any

def load_config(config_path: Path) -> Dict[str, Any]:
    """Loads, expands, and validates the configuration file."""
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    # Basic validation
    if "settings" not in cfg or "commands" not in cfg:
        raise ValueError("Config file is missing 'settings' or 'commands' section.")

    settings = cfg["settings"]
    required_settings = {
        "model_path",
        "target_sample_rate",
        "device_id",
        "buffer_size",
    }
    missing = sorted(required_settings - settings.keys())
    if missing:
        raise ValueError(
            "Config settings missing required key(s): " + ", ".join(missing)
        )

    if not isinstance(settings["model_path"], str) or not settings["model_path"]:
        raise ValueError("Config setting 'model_path' must be a non-empty string.")

    sample_rate = settings["target_sample_rate"]
    if (
        isinstance(sample_rate, bool)
        or not isinstance(sample_rate, (int, float))
        or sample_rate <= 0
    ):
        raise ValueError("Config setting 'target_sample_rate' must be a positive number.")

    buffer_size = settings["buffer_size"]
    if (
        isinstance(buffer_size, bool)
        or not isinstance(buffer_size, int)
        or buffer_size <= 0
    ):
        raise ValueError("Config setting 'buffer_size' must be a positive integer.")

    # Expand tilde in paths for portability
    cfg["settings"]["model_path"] = str(Path(cfg["settings"]["model_path"]).expanduser())
    dynamic = cfg["commands"].get("dynamic", {})
    if dynamic.get("project_manager_path"):
        path = dynamic["project_manager_path"]
        dynamic["project_manager_path"] = str(Path(path).expanduser())

    return cfg
