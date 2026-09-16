# News Briefing

A bounded, auditable morning-briefing pipeline. It acquires public weather, news, and market data, normalizes it into a structured snapshot, asks a configured synthesizer to produce spoken prose, writes the result atomically, and can optionally read it aloud.

## Design

- **Acquisition is separate from synthesis.** Source text is normalized before it reaches the model.
- **External content is untrusted data.** The synthesis prompt forbids following instructions embedded in feeds or API responses.
- **Network access is bounded.** Requests use explicit timeouts and response-size limits.
- **Partial source failures are non-fatal.** Failures are recorded in `errors`; the model is told not to invent missing facts.
- **Market data is optional.** Finnhub is used only when `FINNHUB_API_KEY` is present. CoinGecko remains best-effort.
- **Reuters is optional/configurable.** Set `BRIEF_REUTERS_RSS` only to a currently valid RSS endpoint; no stale endpoint is hardcoded.
- **Speech is optional.** Use `--no-speech` for text-only operation.
- **Snapshots support replay.** `--snapshot-out` records normalized inputs; `--snapshot-in` enables deterministic offline regeneration and testing.

## Requirements

Required: Python 3.11+ and a synthesis command that accepts the prompt as its final argument and prints the briefing to stdout.

Optional:

- `espeak` and `aplay` for spoken output;
- `FINNHUB_API_KEY` for SPY/QQQ/VIXY quotes.

The default synthesizer command is `apex` for compatibility with the original project. Override it with `BRIEF_SYNTH_CMD` or `--synth-command`. The command must return only the generated briefing on stdout and a non-zero exit status on failure.

## Configuration

```bash
export BRIEF_LAT="40.7128"
export BRIEF_LON="-74.0060"
export BRIEF_LOCATION="New York, NY"
export BRIEF_SYNTH_CMD="apex"
# Optional:
export FINNHUB_API_KEY="..."
export BRIEF_REUTERS_RSS="https://example.invalid/current-feed.xml"
```

No personal location is built into the project. Coordinates are required for live acquisition.

## Usage

```bash
./news-briefing.sh --no-speech
./news-briefing.sh --snapshot-out ./snapshot.json --no-speech
./news-briefing.sh --snapshot-in ./snapshot.json --no-speech
```

The default output is `~/brief.txt`; override with `--output` or `BRIEF_OUTPUT`.

For speech, omit `--no-speech`. Voice parameters may be set with `BRIEF_VOICE`, `BRIEF_SPEED`, and `BRIEF_PITCH`.

## Failure behavior

A source outage does not abort the whole briefing; it is recorded in the normalized snapshot and reported as a warning. Configuration, synthesis, output-write, and speech failures return a non-zero exit status. Output is replaced atomically so failed generation does not leave a partial briefing.

The project does not execute source content, shell-expand feed text, or ask the synthesizer to write files or run commands.

## Security boundaries

This tool summarizes public network content. Feed/API text can contain hostile or misleading content and must never be treated as instructions. Model output is generated content, not independently verified reporting. API credentials are read from environment variables and are never written to snapshots or briefing files.

## Validation

All automated validation is offline:

```bash
python3 -m unittest -v tests.test_news_briefing
python3 -m py_compile news_briefing.py
bash -n news-briefing.sh
```

The test suite covers RSS/JSON normalization, prompt-injection boundaries, partial source failure, synthesis failure, atomic output, required configuration, and end-to-end snapshot replay.
