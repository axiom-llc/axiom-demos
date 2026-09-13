# AXIOM Demos

Applied integration examples for AXIOM components and adjacent automation
workflows. Each demo has its own dependencies, configuration, and operational
boundary; these examples are not a shared runtime or deployment product.

![CI](https://github.com/axiom-llc/axiom-demos/actions/workflows/ci.yml/badge.svg)

---

## Included demonstrations

### [logistics-dashboard](./logistics-dashboard/)

Logistics dashboard example using Gemini, Flask, Dash, and SQLite.

### [voice-agent](./voice-agent/)

Voice IVR example using Gemini, Flask, and Twilio. It includes a Dockerfile and
Cloud Run deployment script; deployment is an operator-controlled action.

### [voice-commander](./voice-commander/)

Local workstation voice automation using Vosk and PortAudio. It uses configured
command mappings; review the command configuration before enabling execution.

---

## Tests

```bash
python -m pip install pytest -r voice-agent/requirements.txt -r voice-commander/requirements.txt
python -m pytest tests/ -q
(cd voice-commander && python -m unittest -v test_config.py test_executor.py test_transcriber.py)
```

Smoke tests cover the web-facing demos. Voice Commander has hardware-independent
configuration, transcription-flow, and command-boundary tests. Gemini and Twilio
calls are mocked in CI; microphone and end-to-end telephony delivery remain
manual checks. CI runs on Python 3.11 and 3.12 for pushes and verifies the Voice
Agent Docker build.

---

Built by [AXIOM LLC](https://axiom-llc.github.io)
