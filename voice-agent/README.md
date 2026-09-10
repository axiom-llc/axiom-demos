# Axiom LLC Voice Agent
AI-powered phone IVR system built with Twilio, Gemini, and Flask. Handles inbound calls with a multi-option menu, preset service information, and a live AI assistant for natural-language Q&A about services and past projects.

## Architecture
```
Twilio (inbound call)
    └── Flask (TwiML routing)
            ├── IVR menu (presets 1-7)
            ├── AI assistant (Gemini 2.5 Flash + audio transcription)
            └── Call forwarding + voicemail fallback
```

## Stack
- **Twilio** — telephony, call routing, audio recording
- **Gemini 2.5 Flash Lite** — audio transcription + conversational AI
- **Flask** — TwiML webhook server
- **Gunicorn** — production WSGI
- **Google Cloud Run** — serverless deployment target

## Setup
```bash
pip install -r requirements.txt
export GEMINI_API_KEY="..."
export TWILIO_ACCOUNT_SID="ACxxxx"
export TWILIO_AUTH_TOKEN="..."
export CONTACT_PHONE="+1xxxxxxxxxx"
python main.py
```

## Local Testing
```bash
ngrok http 5000
```
Set `TWILIO_WEBHOOK_BASE_URL=https://<ngrok-url>` before starting Flask when using a proxy or tunnel. Use the public origin exactly as configured in Twilio; forwarded headers are not trusted.

Set Twilio webhook: `Console → Phone Numbers → Voice → Webhook → https://<ngrok-url>/`

## Endpoints
| Route | Description |
|---|---|
| `POST /` | Main IVR menu |
| `POST /route` | Keypress dispatcher |
| `POST /nav` | Menu navigation (repeat/back) |
| `POST /ai` | AI conversation loop |
| `POST /ai_nav` | AI session navigation |
| `POST /voicemail` | Voicemail fallback |

## Deployment
```bash
# Configure PROJECT_ID and SERVICE_NAME in deploy.sh first
bash deploy.sh
```

## IVR Menu
```
1 → Automation services
2 → AI/ML services
3 → DevOps & infrastructure
4 → Data pipeline engineering
5 → Rates & availability
6 → Portfolio & case studies
7 → Contact information
8 → Live AI assistant
9 → Direct team connection
```

## Webhook security

All routes require a valid `X-Twilio-Signature` using `TWILIO_AUTH_TOKEN`.
Missing authentication configuration returns 503; invalid signatures return 403.
Form signatures follow [Twilio’s documented algorithm](https://www.twilio.com/docs/usage/security).
Set `TWILIO_WEBHOOK_BASE_URL` to the public HTTPS origin for Cloud Run as well as tunnels.
Recording downloads accept only HTTPS `api.twilio.com` recording URLs for
`TWILIO_ACCOUNT_SID`, with no redirects, a 15-second socket timeout and an 8 MiB
response limit. AI responses are escaped before insertion into TwiML.
