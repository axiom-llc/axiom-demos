# axiom-demos

Focused demonstrations of applied AI integration and automation delivery.
Each project is self-contained, runnable, and maps to a real client problem.

![CI](https://github.com/axiom-llc/axiom-demos/actions/workflows/ci.yml/badge.svg)

---

## Demos

### [logistics-dashboard](./logistics-dashboard/)

AI-powered operational intelligence dashboard for a logistics company.
Gemini API + Flask REST API + Dash live dashboard + SQLite.
Delivered as a working POC in ~4 hours.

### [voice-agent](./voice-agent/)

AI-powered voice IVR with telephony integration.
Gemini API + Flask + Twilio — automated call handling, AI conversation loop, and intelligent call routing.
Containerized for GCP Cloud Run deployment.

### [voice-commander](./voice-commander/)

Local, offline workstation voice automation.
Vosk + PortAudio — real-time speech recognition, exact command matching, and secure static/dynamic command execution.
Hardware-independent tests cover configuration, transcription flow, and command trust boundaries.

---

## Tests

    pip install pytest -r voice-agent/requirements.txt -r voice-commander/requirements.txt
    pytest tests/ -q
    (cd voice-commander && python -m unittest -v test_config.py test_executor.py test_transcriber.py)

Smoke tests cover the hosted demos, while AXIOM Voice Commander has hardware-independent configuration, transcription-flow, and command-security tests. Gemini and Twilio calls are mocked in CI; microphone validation remains manual. CI runs on Python 3.11 and 3.12 on every push, plus a Docker build verification of the voice agent image.

---

Built by [AXIOM LLC](https://axiom-llc.github.io)
