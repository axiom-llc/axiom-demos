#!/usr/bin/env python3
"""Minimal Gemini synthesis adapter for news-briefing."""
import os
import sys

from google import genai

DEFAULT_MODEL = "gemini-3.8-flash"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: gemini-synth.py PROMPT", file=sys.stderr)
        return 2
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("gemini-synth: GEMINI_API_KEY is required", file=sys.stderr)
        return 2
    model = os.getenv("BRIEF_GEMINI_MODEL", DEFAULT_MODEL)
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=sys.argv[1],
        )
        text = response.text
    except Exception as exc:
        print(f"gemini-synth: generation failed: {exc}", file=sys.stderr)
        return 1
    if not text or not text.strip():
        print("gemini-synth: Gemini returned no text", file=sys.stderr)
        return 1
    print(text.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
