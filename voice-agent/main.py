from flask import Flask, request, Response, abort
import re
from xml.sax.saxutils import escape
import os
import requests
from google import genai
from google.genai import types
from twilio.request_validator import RequestValidator

app = Flask(__name__)
client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY"),
    http_options=types.HttpOptions(timeout=60000, retry_options=types.HttpRetryOptions(attempts=1)),
)
conversations = {}


@app.before_request
def verify_twilio_request():
    """Authenticate Twilio form webhooks before routing or outbound requests."""
    if request.method != "POST":
        return None

    token = os.environ.get("TWILIO_AUTH_TOKEN", "")
    if not token:
        abort(503, description="Twilio authentication is not configured")

    base_url = os.environ.get("TWILIO_WEBHOOK_BASE_URL", "").rstrip("/")
    path = request.full_path if request.query_string else request.path
    url = base_url + path if base_url else request.url
    signature = request.headers.get("X-Twilio-Signature", "")

    if not signature or not RequestValidator(token).validate(
        url,
        request.form,
        signature,
    ):
        abort(403)

    return None


def _recording_url_allowed(url, account_sid):
    # Credentials must only go to this account's Twilio recording endpoint.
    return bool(account_sid and re.fullmatch(
        r"https://api\.twilio\.com/2010-04-01/Accounts/"
        + re.escape(account_sid) + r"/Recordings/RE[0-9a-fA-F]{32}(?:\.wav)?",
        url,
    ))

SYSTEM_PROMPT = """You are Axiom LLC's AI assistant helping potential clients understand our services.

SERVICES:
1. Python/Bash Automation — production scripts, zero-dependency design, 24-72hr delivery
2. AI Agent Orchestration — Gemini Pro, Ollama, multi-agent systems, self-correcting logic
3. Data Pipeline Engineering — ETL, PostgreSQL, API connectors, 100% error detection frameworks
4. DevOps/Infrastructure — GCP, Docker, CI/CD, Arch Linux, system monitoring

KEY RESULTS:
- Multi-agent orchestration: zero-regression deployments, advanced meta-prompting
- 4-hour logistics dashboard POC (Gemini + Flask + Dash) → $15K contract
- DevOps automation: 15hrs → 2hrs/week ops, 99.98% reliability, 87% auto-remediation
- Insurance workflow automation: 75% processing time reduction
- RESTful API framework: 2-week → 3-day integration timeline

STACK: Python, Bash, C, SQL | Gemini Pro, Ollama | PostgreSQL, Flask | Docker, GCP, Git | React, Dash

BUSINESS:
- Rate: $35/hr, fixed-price preferred for defined scope
- Availability: 20-40 hrs/week EST, immediate start
- Delivery: 24-72hrs typical; fastest: 4hrs full POC
- Response: 12hrs on business days
- Portfolio: github.com/axiom-llc

STYLE: professional, technical, metrics-driven. Cite delivered results. For project inquiries gather:
scope, timeline, budget, technical requirements. Direct hire-ready callers to press 9 to speak with our team."""

MENU = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather action="/route" numDigits="1" timeout="7">
        <Say>
            Welcome to Axiom L L C.
            Press 1 for automation services.
            Press 2 for A I and machine learning.
            Press 3 for DevOps and infrastructure.
            Press 4 for data pipeline engineering.
            Press 5 for rates and availability.
            Press 6 for portfolio and case studies.
            Press 7 for contact information.
            Press 8 to speak with our A I assistant.
            Press 9 to connect directly with our team.
        </Say>
    </Gather>
    <Hangup/>
</Response>"""

PRESETS = {
    "1": """Python and Bash automation services include: production-ready scripts for data processing and system administration.
            Workflow optimization with zero-dependency design. ETL automation for CSV and Excel transformation.
            Comprehensive error handling and logging. Cron and Systemd scheduling. Standard delivery 24 to 72 hours.
            Recent project delivered 30 percent efficiency improvement and 75 percent processing time reduction
            for insurance benefits administration.""",

    "2": """A I and machine learning services include: multi-agent orchestration using Gemini Pro and Ollama.
            L L M integration with self-correcting logic and deterministic execution. Prompt engineering and N L P.
            Research automation and intelligent data extraction.
            Recent project: 4-hour proof of concept A I logistics dashboard using Gemini, Flask, and Dash,
            which led to a 15 thousand dollar implementation contract.""",

    "3": """DevOps and infrastructure services include: Google Cloud Platform optimization and cost reduction.
            C I C D pipelines. Docker containerization. Infrastructure monitoring and system administration.
            Comprehensive Arch Linux expertise.
            Recent project: production DevOps automation suite reduced weekly manual operations from 15 hours to 2 hours,
            achieving 99.98 percent sync reliability and 87 percent auto-remediation without manual intervention.""",

    "4": """Data pipeline engineering services include: E T L workflow design and implementation. PostgreSQL integration.
            A P I connector development with RESTful design. CSV and Excel transformation at scale.
            Probabilistic quality assurance achieving 100 percent error detection for mission-critical operations.
            Flask backend development with comprehensive data validation.
            Recent projects include enterprise-scale pipelines with zero data loss.""",

    "5": """Rate structure: 35 dollars per hour. Fixed-price arrangements preferred for defined project scope.
            Volume discounts available for ongoing or multi-project engagements.
            Availability: immediate, 20 to 40 hours per week, Eastern Time.
            Response time: within 12 hours on business days.
            Standard turnaround: 24 to 72 hours. Fastest delivery: complete 4-hour proof of concept.""",

    "6": """Portfolio highlights: multi-agent orchestration with Gemini Pro, zero-regression production deployments.
            A I logistics dashboard POC in under 4 hours leading to a 15 thousand dollar contract.
            Production DevOps automation suite with 99.98 percent reliability over 12 months.
            RESTful A P I integration framework reducing timelines from 2 weeks to 3 days.
            Full portfolio at github dot com slash axiom dash L L C.""",

    "7": """Contact: visit github dot com slash axiom dash L L C for portfolio and open source projects.
            For project inquiries, press 9 to connect with our team directly,
            or press 8 to speak with our A I assistant and describe your requirements.""",
}


@app.route("/", methods=["POST"])
def main_menu():
    return Response(MENU, mimetype="text/xml")


@app.route("/route", methods=["POST"])
def route():
    digit = request.form.get("Digits")

    if digit in PRESETS:
        return Response(f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>{PRESETS[digit]}</Say>
    <Say>Press star to return to the main menu, or press pound to repeat.</Say>
    <Gather action="/nav" numDigits="1" timeout="4" finishOnKey="*#"/>
    <Redirect>/</Redirect>
</Response>""", mimetype="text/xml")

    elif digit == "8":
        return Response("""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Connecting to Axiom's A I assistant. Speak after the beep.</Say>
    <Record action="/ai" maxLength="30" playBeep="true"/>
</Response>""", mimetype="text/xml")

    elif digit == "9":
        return Response(f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Connecting you to our team now. Please hold.</Say>
    <Dial timeout="25" action="/voicemail">
        <Number>{escape(os.environ.get("CONTACT_PHONE", ""))}</Number>
    </Dial>
</Response>""", mimetype="text/xml")

    return Response('<Response><Redirect>/</Redirect></Response>', mimetype="text/xml")


@app.route("/nav", methods=["POST"])
def nav():
    digit = request.form.get("Digits")
    if digit == "#":
        return Response('<Response><Redirect>/route</Redirect></Response>', mimetype="text/xml")
    return Response('<Response><Redirect>/</Redirect></Response>', mimetype="text/xml")


@app.route("/ai", methods=["POST"])
def ai_conversation():
    caller = request.form.get("From", "unknown")
    recording_url = request.form.get("RecordingUrl")

    if not recording_url:
        return Response('<Response><Redirect>/</Redirect></Response>', mimetype="text/xml")

    account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
    if not _recording_url_allowed(recording_url, account_sid):
        abort(400, description="Invalid recording URL")

    try:
        with requests.get(
            recording_url,
            auth=(account_sid, os.environ["TWILIO_AUTH_TOKEN"]),
            timeout=15, allow_redirects=False, stream=True,
        ) as audio:
            if audio.status_code != 200:
                raise ValueError("Recording download failed")
            audio_bytes = bytearray()
            for chunk in audio.iter_content(chunk_size=65536):
                audio_bytes.extend(chunk)
                if len(audio_bytes) > 8 * 1024 * 1024:
                    raise ValueError("Recording exceeds 8 MiB")

        if caller not in conversations:
            conversations[caller] = []

        contents = conversations[caller].copy()
        contents.append(types.Content(
            parts=[
                types.Part.from_bytes(data=bytes(audio_bytes), mime_type="audio/wav"),
                types.Part(text="Transcribe and respond conversationally.")
            ],
            role="user"
        ))

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
        )

        ai_text = response.text.strip()
        conversations[caller].append(types.Content(parts=[types.Part(text=ai_text)], role="model"))

        if len(conversations[caller]) > 20:
            conversations[caller] = conversations[caller][-20:]

        return Response(f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>{escape(ai_text)}</Say>
    <Say>Press star for main menu, press 9 to connect with our team, or continue speaking.</Say>
    <Gather action="/ai_nav" numDigits="1" timeout="2" finishOnKey="*9"/>
    <Record action="/ai" maxLength="30" playBeep="true"/>
</Response>""", mimetype="text/xml")

    except Exception:
        app.logger.error("Voice provider operation failed")
        return Response('<Response><Say>An error occurred.</Say><Redirect>/</Redirect></Response>', mimetype="text/xml")


@app.route("/ai_nav", methods=["POST"])
def ai_nav():
    digit = request.form.get("Digits")
    if digit == "*":
        return Response('<Response><Redirect>/</Redirect></Response>', mimetype="text/xml")
    elif digit == "9":
        return Response(f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Transferring you to our team now.</Say>
    <Dial timeout="25" action="/voicemail">
        <Number>{escape(os.environ.get("CONTACT_PHONE", ""))}</Number>
    </Dial>
</Response>""", mimetype="text/xml")
    return ai_conversation()


@app.route("/voicemail", methods=["POST"])
def voicemail():
    if request.form.get("DialCallStatus") in ["no-answer", "busy", "failed"]:
        return Response("""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Our team is currently unavailable. Please leave a detailed message including your name,
    contact information, project type, timeline, and budget. Messages are reviewed within 12 hours on business days.</Say>
    <Record maxLength="180" playBeep="true"/>
    <Say>Thank you for contacting Axiom L L C. We will follow up within 12 hours on business days.</Say>
</Response>""", mimetype="text/xml")
    return Response('<Response><Hangup/></Response>', mimetype="text/xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
