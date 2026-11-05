# AXIOM Demos

Advanced AI applications, systems integrations, deterministic robotics simulation and engineering utilities from AXIOM. Each project includes its own entry points, dependencies and reproducible tests.

## Public engineering editions

### [cybernetics](./cybernetics/)

Deterministic robotics simulation: authorization binding, safety envelopes, fault injection, telemetry and tamper-evident receipts.

### [ops](./ops/)

Reusable document, structured-text and media utilities with native regression tests.

[Source provenance](SOURCES.json) records the exact imported engineering files.

### [blender](./blender/)

Declarative 3D scene automation with JSON-controlled materials, lighting and camera configuration. Original source and reference render retained.

## Included demonstrations

### [core-stack](./core-stack/)

Canonical deterministic ASON → APEX → RAG reference. It delegates execution to `axiom-infra/core_stack.py`, verifies durable authorization/plan binding, exercises the RAG HTTP boundary without provider generation, and emits revision-bound evidence.

### [organizational-simulations](./organizational-simulations/)

Five thin wrappers for evidence-backed synthetic organizational simulations spanning robotics production, software development, specialty-care administration, SOC operations, and logistics/supply chain. Canonical models and retained evidence remain in `axiom-research`; fresh runs write outside the repository by default.

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

Bounded news aggregation and Gemini synthesis demo with Open-Meteo current conditions
and five-day forecasts, normalized source snapshots, optional market data, spoken output,
offline replay, and explicit untrusted-content boundaries.

---

## Development and validation

```bash
python -m pip install pytest -r voice-agent/requirements.txt -r voice-commander/requirements.txt -r news-briefing/requirements.txt
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

[AXIOM LLC](https://axiom-llc.github.io) · Advanced systems engineering and runnable demonstrations.

## Consolidated example ownership — November 5, 2026

[Blender](blender/) and [Infinite Wiki](wiki/) are developed here. Their original repositories are archived; source history, release URLs and compatibility links remain preserved. Wiki's complete five-file tree, including its original favicon and browser regression, is imported unchanged. Blender's complete code/configuration/license/reference render is retained; the intentional README presentation differs from its source archive. Original public source ancestry and all source branch/tag tips are preserved in this repository. See [consolidation manifest](consolidation-2026-11-05.json).

Use the per-example requirements and test commands. Blender requires its documented5.2LTS runtime; availability of a different Blender version is not equivalent validation. No independent source-repository development or duplicate demo repository is needed.
