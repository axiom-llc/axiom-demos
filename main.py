#!/usr/bin/env python3
# voice-commander/main.py
"""
A configurable, real-time voice command application that executes shell
commands based on spoken input.

Usage:
    python main.py
    python main.py --config /path/to/commands.json
"""

import argparse
import sys
from pathlib import Path

import config
import executor
import transcriber


def main() -> None:
    parser = argparse.ArgumentParser(description="A real-time, configurable voice commander.")
    parser.add_argument(
        "-c", "--config", type=Path,
        default=Path(__file__).parent / "commands.json",
        help="Path to the JSON configuration file."
    )
    args = parser.parse_args()

    try:
        app_config = config.load_config(args.config)
        settings = app_config["settings"]
        commands = app_config["commands"]

        command_executor = executor.CommandExecutor(commands)
        live_transcriber = transcriber.LiveTranscriber(settings)

        for transcribed_text in live_transcriber.start_stream():
            command_executor.execute(transcribed_text)

    except FileNotFoundError as e:
        print(f"FATAL ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStopping via Ctrl+C.", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected fatal error occurred: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
