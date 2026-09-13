# Logistics dashboard demo

Prototype operational dashboard built from sample shipment data. It combines a
local SQLite database, a small Flask API, Dash/Plotly views, and optional Gemini
analysis. It is an applied example, not a logistics product or a production
deployment.

## What it demonstrates

- CSV ingestion and calculated delivery/fuel metrics;
- a Flask JSON API for summary and per-partner views;
- a Dash dashboard that reads that API; and
- optional Gemini-powered contract-compliance and scenario views using synthetic
  contracts.

The ingestion script also requests synthetic partner-task data from
JSONPlaceholder. That request is an external demo dependency, not a partner
integration or reliability guarantee.

## Requirements and setup

Use Python 3.11 or 3.12, as used by the portfolio CI. Install the demo's direct
dependencies in an isolated environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install pandas requests flask dash dash-bootstrap-components plotly google-genai
```

Set `GEMINI_API_KEY` only before using `compliance_dashboard.py`. The local
ingestion/API/dashboard path does not need it.

## Run

From this directory, create the local database first:

```bash
python data_ingestion.py
python operations_api.py
```

In a second terminal, start the dashboard:

```bash
python live_dashboard.py
```

`demo.sh` starts the ingestion, API, and dashboard sequence. The individual
commands are preferable when inspecting failures or stopping a single process.

The Flask API listens on port 5000 and exposes:

```text
GET /api/logistics/daily_summary
GET /api/partner_performance/status?partner_contract=Amazon-Prime
```

Run `python compliance_dashboard.py` separately for the optional Gemini view.
It listens on port 8051; the Dash operational view uses port 8050.

## Boundaries

The checked-in CSV, partner names, contracts, and task-health data are sample or
synthetic. SQLite is a local demo database. The code has no authentication,
multi-user access control, production data contract, background job system, or
deployment-hardening claim. Provider failures are displayed generically; Gemini
calls use one attempt and a 60-second HTTP timeout. Keep provider credentials
out of source control and CI.

## Validation

The portfolio suite smoke-tests web-facing demo behavior on Python 3.11 and
3.12. Provider calls are mocked in CI. A live provider check or availability of
JSONPlaceholder is not established by those tests.
