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

    # Expand tilde in paths for portability
    cfg["settings"]["model_path"] = str(Path(cfg["settings"]["model_path"]).expanduser())
    dynamic = cfg["commands"].get("dynamic", {})
    if dynamic.get("project_manager_path"):
        path = dynamic["project_manager_path"]
        dynamic["project_manager_path"] = str(Path(path).expanduser())

    return cfg
