# AXIOM Demos

Applied integration examples for AXIOM components and adjacent automation
workflows. Each demo has its own dependencies, configuration, and operational
boundary; these examples are not a shared runtime or deployment product.

## Included demonstrations

### [logistics-dashboard](./logistics-dashboard/)

Prototype dashboard using sample shipment data, a public placeholder API,
Flask, Dash, SQLite, and an optional Gemini analysis view.

### [voice-agent](./voice-agent/)

Twilio webhook/IVR example using Flask and optional Gemini audio analysis. It
includes a Dockerfile and Cloud Run script, but deployment and telephony
configuration remain operator-controlled.

### [voice-commander](./voice-commander/)

Local workstation voice automation using Vosk and PortAudio. It executes trusted
static command strings from local configuration; review that configuration before
enabling it.

### [news-briefing](./news-briefing/)

Bounded news aggregation and AI synthesis demo with normalized source snapshots,
optional market data and speech, offline replay, and explicit untrusted-content boundaries.

---

## Development and validation

```bash
python -m pip install pytest -r voice-agent/requirements.txt -r voice-commander/requirements.txt
python -m pytest tests/ -q
(cd voice-commander && python -m unittest -v test_config.py test_executor.py test_transcriber.py)
(cd news-briefing && make test)
```

Smoke tests cover the web-facing examples. Voice Commander has
hardware-independent configuration, transcription-flow, and command-boundary
tests. News Briefing has offline acquisition, normalization, prompt-boundary, replay,
and output tests. CI runs on Python 3.11 and 3.12, mocks Gemini and Twilio interactions,
and builds the Voice Agent image. A microphone, live provider calls, public
webhook reachability, and end-to-end telephony are outside that coverage.

---

[AXIOM LLC](https://axiom-llc.github.io) · Examples, not a shared production runtime.
