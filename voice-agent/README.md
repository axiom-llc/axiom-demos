# AXIOM Voice Agent demo

Flask/TwiML example for a Twilio phone menu with optional Gemini-assisted audio
responses. It demonstrates webhook routing, request-signature validation,
recording handling, and a simple in-memory conversation history. It is a demo,
not a managed telephony service or a claim of end-to-end call reliability.

## Requirements

Use Python 3.11 and install the pinned application dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Configure these values for the complete recording, AI, and forwarding flow.
`TWILIO_AUTH_TOKEN` is required for every webhook request:

```bash
export GEMINI_API_KEY='...'
export TWILIO_ACCOUNT_SID='AC...'
export TWILIO_AUTH_TOKEN='...'
export CONTACT_PHONE='+1...'
```

For a public deployment or tunnel, also set `TWILIO_WEBHOOK_BASE_URL` to the
exact public HTTPS origin registered with Twilio. The application does not trust
forwarded headers to reconstruct that origin.

## Run and connect

```bash
python main.py
```

For a local tunnel, expose port 5000 and configure Twilio's Voice webhook with
the resulting `https://…/` URL. For example:

```bash
ngrok http 5000
export TWILIO_WEBHOOK_BASE_URL='https://your-tunnel.example'
```

Use the configured public origin exactly in Twilio and in
`TWILIO_WEBHOOK_BASE_URL`; it participates in signature validation.

The application accepts these POST routes: `/`, `/route`, `/nav`, `/ai`,
`/ai_nav`, and `/voicemail`. The menu provides preset responses, recording-based
AI interaction, forwarding to `CONTACT_PHONE`, and a voicemail fallback.

## Security and operating boundaries

Every POST route requires a valid `X-Twilio-Signature`. Missing authentication
configuration returns 503; invalid or missing signatures return 403. Recording
downloads are restricted to HTTPS `api.twilio.com` URLs for the configured
account, use no redirects, have a 15-second socket timeout, and stop at 8 MiB.
Dynamic TwiML text is escaped.

Gemini calls use `gemini-3.5-flash-lite`, one attempt, and a 60-second timeout.
Errors are logged generically rather than exposing provider response bodies.
Conversation history is process-local memory; it is not durable and is not safe
for multi-worker session continuity. The example does not provide rate limiting,
data retention controls, consent handling, delivery monitoring, or a production
security review. Keep Twilio and Gemini credentials out of CI and source control.

## Container and deployment

The Dockerfile runs Gunicorn with one worker. `deploy.sh` is a convenience script
for an operator who has already configured a Google Cloud project, service name,
credentials, and required environment variables. Running it creates or updates
hosted resources; it is not part of local validation and should be reviewed
before use.

Portfolio CI mocks Gemini and Twilio behavior and verifies that the image builds.
It does not validate a reachable public webhook, an inbound call, recording
delivery, or live Gemini/Twilio credentials.
