# News Briefing

A bounded, auditable morning-briefing pipeline. It acquires public weather, news, and market data, normalizes it into a structured snapshot, synthesizes concise spoken prose with Gemini, writes the result atomically, and can optionally read it aloud.

## Design

- **Acquisition is separate from synthesis.** Source text is normalized before it reaches the model.
- **External content is untrusted data.** The synthesis prompt forbids following instructions embedded in feeds or API responses.
- **Network access is bounded.** Requests use explicit timeouts and response-size limits.
- **Partial source failures are non-fatal.** Failures are recorded in `errors`; unavailable data is distinguished from confirmed absence.
- **Market data is optional.** Finnhub is used only when `FINNHUB_API_KEY` is present. CoinGecko remains best-effort.
- **Reuters discovery is optional/configurable.** `BRIEF_REUTERS_RSS` may point to an HTTPS RSS endpoint; the example uses a Google News query constrained to Reuters URLs and is not an official Reuters feed.
- **Speech is optional.** Use `--no-speech` for text-only operation.
- **Snapshots support replay.** `--snapshot-out` records normalized inputs; `--snapshot-in` enables deterministic offline regeneration and testing.

## Requirements

Required:

- Python 3.11+;
- `google-genai`;
- `GEMINI_API_KEY`.

The bundled `gemini-synth.py` adapter is the default synthesizer and uses `gemini-3.8-flash`. Override the model with `BRIEF_GEMINI_MODEL`, or replace the synthesis backend with `BRIEF_SYNTH_CMD` / `--synth-command`. A replacement command must accept the prompt as its final argument, print only the generated briefing to stdout, and return non-zero on failure.

Gemini API quotas and pricing are controlled by the Google API project/account, not this program. `gemini-3.8-flash` can be used under Google's Free Tier subject to its current eligibility and quotas; this project does not enable billing or guarantee that a particular API project is non-billable. Verify the API project's tier before relying on zero-cost operation.

Optional:

- `espeak` and `aplay` for spoken output;
- `FINNHUB_API_KEY` for SPY/QQQ/VIXY quotes.

## Configuration

```bash
export GEMINI_API_KEY="..."
export BRIEF_LAT="40.268368"
export BRIEF_LON="-74.505238"
export BRIEF_LOCATION="East Windsor, NJ"
# Optional:
# export BRIEF_GEMINI_MODEL="gemini-3.8-flash"
# export FINNHUB_API_KEY=""
export BRIEF_REUTERS_RSS="https://news.google.com/rss/search?q=site%3Areuters.com%20when%3A1d&hl=en-US&gl=US&ceid=US%3Aen"
```

No personal location or API credential is built into the project. Coordinates are required for live acquisition.

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

Automated validation is offline:

```bash
python3 -m unittest -v tests.test_news_briefing
python3 -m py_compile news_briefing.py gemini-synth.py
bash -n news-briefing.sh
```

The test suite covers RSS/JSON normalization, prompt-injection boundaries, partial source failure, synthesis failure, atomic output, required configuration, the default Gemini adapter boundary, and end-to-end snapshot replay.
