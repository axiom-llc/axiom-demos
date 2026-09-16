# News Briefing

A bounded, auditable morning-briefing pipeline. It acquires public weather, news, and market data, normalizes it into a structured snapshot, synthesizes concise spoken prose with Gemini, writes the result atomically, and reads it aloud by default.

## Design

- **Acquisition is separate from synthesis.** Source text is normalized before it reaches the model.
- **Weather uses Open-Meteo.** Live coordinates drive current conditions plus a five-day forecast: temperature, apparent temperature, humidity, wind, pressure, WMO condition, daily high/low, and precipitation probability. Weather alerts are not acquired.
- **External content is untrusted data.** The synthesis prompt forbids following instructions embedded in feeds or API responses.
- **Network access is bounded.** Requests use explicit timeouts and a 1 MB response-size limit.
- **Partial source failures are non-fatal.** Failures are recorded in `errors`; unavailable sections remain explicit to synthesis.
- **Market data is optional.** Finnhub supplies SPY/QQQ/VIXY only when `FINNHUB_API_KEY` is present; CoinGecko Bitcoin acquisition remains best-effort.
- **News sources are bounded.** Technology uses Hacker News, Lobsters, and recent GitHub repositories; world news uses BBC plus optional `BRIEF_REUTERS_RSS`.
- **Reuters discovery is configurable.** The example RSS value is a Google News query constrained to Reuters URLs, not an official Reuters feed.
- **Speech is enabled by default.** `espeak` generates WAV audio and `aplay` plays it; use `--no-speech` for text-only operation.
- **Snapshots support replay.** `--snapshot-out` records normalized inputs; `--snapshot-in` replays saved acquisition data without source-network calls; synthesis still uses the configured backend.

## Requirements

Required for the default live workflow:

- Python 3.11+;
- `google-genai==1.66.0` (the verified dependency version; install with `python -m pip install -r requirements.txt`);
- `GEMINI_API_KEY`;
- `BRIEF_LAT` and `BRIEF_LON`;
- `espeak` and `aplay` for the default spoken-output path.

The bundled executable `gemini-synth.py` is the default synthesizer and uses `gemini-3.8-flash`. Override only the model with `BRIEF_GEMINI_MODEL`, or replace the synthesis backend with `BRIEF_SYNTH_CMD` / `--synth-command`. A replacement command must accept the complete prompt as its final argument, print only the generated briefing to stdout, and return non-zero on failure.

Gemini API quotas and pricing are controlled by the Google API project/account, not this program. The project does not enable billing or guarantee zero-cost operation; verify the API project's current tier and quotas independently.

`espeak` and `aplay` are unnecessary when every run uses `--no-speech`. `FINNHUB_API_KEY` is optional and enables SPY/QQQ/VIXY quotes.

## Configuration

```bash
export GEMINI_API_KEY="..."
export BRIEF_LAT="40.7128"
export BRIEF_LON="-74.0060"
export BRIEF_LOCATION="New York, NY"

# Optional overrides:
# export BRIEF_GEMINI_MODEL="gemini-3.8-flash"
# export BRIEF_OUTPUT="$HOME/brief.txt"
# export BRIEF_HTTP_TIMEOUT="8"
# export BRIEF_VOICE="en+m3"
# export BRIEF_SPEED="149"
# export BRIEF_PITCH="38"
# export FINNHUB_API_KEY="..."
export BRIEF_REUTERS_RSS="https://news.google.com/rss/search?q=site%3Areuters.com%20when%3A1d&hl=en-US&gl=US&ceid=US%3Aen"
```

No personal location or API credential is built into the project. `BRIEF_LOCATION` controls the spoken location label and defaults to `your area`; coordinates control weather acquisition. `NEWS_BRIEFING_USER_AGENT` can override the HTTP User-Agent. `BRIEF_REUTERS_RSS`, when set, must use HTTPS.

## Usage

Run the complete live path, including speech:

```bash
./news-briefing.sh
```

Text-only operation:

```bash
./news-briefing.sh --no-speech
```

Record normalized acquisition data or replay a saved snapshot:

```bash
./news-briefing.sh --snapshot-out ./snapshot.json --no-speech
./news-briefing.sh --snapshot-in ./snapshot.json --no-speech
```

The default output is `~/brief.txt`; override it with `--output` or `BRIEF_OUTPUT`. Command-line `--lat`, `--lon`, `--location`, `--output`, `--timeout`, and `--synth-command` override their corresponding defaults/environment values.

## Failure behavior

A source outage does not abort the whole briefing; it is recorded in the normalized snapshot and reported as a warning after successful generation. Invalid configuration, synthesis failure, output-write failure, or speech failure returns a non-zero exit status. Output replacement is atomic, so a failed write does not leave a partial briefing.

The project does not execute source content, shell-expand feed text, or ask the synthesizer to write files or run commands. Snapshot fields and item lengths are bounded before synthesis.

## Security boundaries

This tool summarizes public network content. Feed/API text can contain hostile, inaccurate, or misleading content and must never be treated as instructions. Model output is generated content, not independently verified reporting. API credentials are read from environment variables and are never written to snapshots or briefing files.

## Validation

Offline validation:

```bash
make test
```

Equivalent commands:

```bash
python3 -m py_compile news_briefing.py gemini-synth.py
bash -n news-briefing.sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_news_briefing
```

The suite covers RSS parsing, coordinate validation, Open-Meteo normalization, snapshot bounds, prompt-injection boundaries, partial acquisition failure, synthesis failure, atomic output, required live configuration, the bundled Gemini default, and end-to-end snapshot replay.

A live end-to-end run additionally requires network access, valid provider configuration, and—unless `--no-speech` is used—a working local audio path. The implementation at commit `b2db460` was verified from a fresh clone on 2026-09-16: all 13 tests passed, live Open-Meteo/Gemini generation wrote `~/brief.txt`, and spoken output was heard successfully.
