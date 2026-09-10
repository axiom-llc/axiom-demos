"""Smoke tests for the Axiom LLC AI Voice IVR (voice-agent/main.py).

The app has a module-level genai.Client() call that fires on import.
We set GEMINI_API_KEY in the environment (CI sets it to a dummy value)
and patch the client before any live calls can be made.

All Twilio webhook calls, Gemini API calls, and outbound HTTP requests
are mocked. No network access required.
"""
from __future__ import annotations
import base64
import hashlib
import hmac
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Ensure the voice-agent directory is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "voice-agent"))


@pytest.fixture(scope="module", autouse=True)
def patch_genai_client():
    """Patch genai.Client before the module is imported so the module-level
    client instantiation doesn't attempt a live API call."""
    mock_response = MagicMock()
    mock_response.text = "Thank you for contacting Axiom LLC."
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    with patch.dict(os.environ, {"TWILIO_AUTH_TOKEN": "test-token", "TWILIO_ACCOUNT_SID": "AC" + "1" * 32, "TWILIO_WEBHOOK_BASE_URL": ""}), patch("google.genai.Client", return_value=mock_client):
        yield mock_client


@pytest.fixture(scope="module")
def client():
    import importlib
    import main as voice_main
    importlib.reload(voice_main)   # reload so patched client takes effect
    voice_main.app.config["TESTING"] = True
    class SignedClient:
        def post(self, path, data=None):
            data = data or {}
            payload = "http://localhost" + path + "".join(k + data[k] for k in sorted(data))
            signature = base64.b64encode(hmac.new(b"test-token", payload.encode(), hashlib.sha1).digest()).decode()
            return voice_main.app.test_client().post(path, data=data, headers={"X-Twilio-Signature": signature})
    return SignedClient()


# ── Main menu ──────────────────────────────────────────────────────────────

class TestMainMenu:
    def test_post_returns_twiml(self, client):
        r = client.post("/")
        assert r.status_code == 200
        assert b"<Response>" in r.data
        assert b"<Gather" in r.data

    def test_response_content_type_is_xml(self, client):
        r = client.post("/")
        assert "xml" in r.content_type


# ── Routing ────────────────────────────────────────────────────────────────

class TestRoute:
    @pytest.mark.parametrize("digit", ["1", "2", "3", "4", "5", "6", "7"])
    def test_preset_digits_return_say_verb(self, client, digit):
        r = client.post("/route", data={"Digits": digit})
        assert r.status_code == 200
        assert b"<Say>" in r.data

    def test_digit_8_returns_record_verb(self, client):
        r = client.post("/route", data={"Digits": "8"})
        assert r.status_code == 200
        assert b"<Record" in r.data

    def test_digit_9_returns_dial_verb(self, client):
        r = client.post("/route", data={"Digits": "9"})
        assert r.status_code == 200
        assert b"<Dial" in r.data  # matches <Dial> and <Dial attr="...">

    def test_unknown_digit_redirects_to_root(self, client):
        r = client.post("/route", data={"Digits": "0"})
        assert r.status_code == 200
        assert b"<Redirect>" in r.data


# ── Navigation ─────────────────────────────────────────────────────────────

class TestNav:
    def test_pound_repeats_route(self, client):
        r = client.post("/nav", data={"Digits": "#"})
        assert r.status_code == 200
        assert b"<Redirect>/route</Redirect>" in r.data

    def test_star_returns_to_menu(self, client):
        r = client.post("/nav", data={"Digits": "*"})
        assert r.status_code == 200
        assert b"<Redirect>/</Redirect>" in r.data


# ── AI conversation ────────────────────────────────────────────────────────

class TestAIConversation:
    def test_missing_recording_url_redirects(self, client):
        r = client.post("/ai", data={"From": "+15551234567"})
        assert r.status_code == 200
        assert b"<Redirect>" in r.data

    def test_recording_url_triggers_ai_response(self, client):
        with patch("requests.get") as mock_get:
            audio = mock_get.return_value.__enter__.return_value
            audio.status_code = 200
            audio.iter_content.return_value = [b"fake-audio-bytes"]
            r = client.post("/ai", data={
                "From": "+15551234567",
                "RecordingUrl": "https://api.twilio.com/2010-04-01/Accounts/AC11111111111111111111111111111111/Recordings/RE22222222222222222222222222222222",
            })
        assert r.status_code == 200
        assert b"<Say>" in r.data


# ── Voicemail ──────────────────────────────────────────────────────────────

class TestVoicemail:
    def test_no_answer_triggers_voicemail(self, client):
        r = client.post("/voicemail", data={"DialCallStatus": "no-answer"})
        assert r.status_code == 200
        assert b"<Record" in r.data

    def test_completed_call_hangs_up(self, client):
        r = client.post("/voicemail", data={"DialCallStatus": "completed"})
        assert r.status_code == 200
        assert b"<Hangup/>" in r.data


@pytest.mark.parametrize("path", ["/", "/route", "/nav", "/ai", "/ai_nav", "/voicemail"])
def test_unsigned_webhooks_rejected(client, path):
    import main
    with patch("requests.get") as get:
        assert main.app.test_client().post(path).status_code == 403
    get.assert_not_called()


@pytest.mark.parametrize("url", [
    "https://attacker.invalid/recording", "http://127.0.0.1/",
    "https://api.twilio.com.attacker.invalid/recording",
    "https://api.twilio.com@attacker.invalid/recording",
    "https://api.twilio.com/2010-04-01/Accounts/other/Recordings/RE" + "2" * 32,
])
def test_recording_credentials_never_sent_to_untrusted_url(client, url):
    with patch("requests.get") as get:
        assert client.post("/ai", data={"RecordingUrl": url}).status_code == 400
    get.assert_not_called()


def test_missing_auth_configuration_fails_closed(client):
    import main
    with patch.dict(os.environ, {"TWILIO_AUTH_TOKEN": ""}):
        assert main.app.test_client().post("/").status_code == 503


def test_tampered_signature_rejected(client):
    import main
    assert main.app.test_client().post("/ai", headers={"X-Twilio-Signature": "invalid"}).status_code == 403


def test_public_webhook_url_behind_proxy(client):
    import main
    url = "https://voice.example.com/route?source=call"
    payload = url + "Digits1"
    signature = base64.b64encode(hmac.new(b"test-token", payload.encode(), hashlib.sha1).digest()).decode()
    with patch.dict(os.environ, {"TWILIO_WEBHOOK_BASE_URL": "https://voice.example.com"}):
        response = main.app.test_client().post("/route?source=call", data={"Digits": "1"}, headers={"X-Twilio-Signature": signature})
    assert response.status_code == 200


def test_download_is_bounded_and_ai_output_is_xml_text(client, patch_genai_client):
    import xml.etree.ElementTree as ET
    url = "https://api.twilio.com/2010-04-01/Accounts/AC" + "1" * 32 + "/Recordings/RE" + "2" * 32
    patch_genai_client.models.generate_content.return_value.text = "Hello & <Dial>untrusted</Dial>"
    try:
        with patch("requests.get") as get:
            audio = get.return_value.__enter__.return_value
            audio.status_code = 200
            audio.iter_content.return_value = [b"audio"]
            response = client.post("/ai", data={"RecordingUrl": url})
        assert get.call_args.kwargs["allow_redirects"] is False
        assert get.call_args.kwargs["timeout"] == 15
        assert get.call_args.kwargs["stream"] is True
        root = ET.fromstring(response.data)
        assert root.find("Say").text == "Hello & <Dial>untrusted</Dial>"
        assert root.find(".//Dial") is None
    finally:
        patch_genai_client.models.generate_content.return_value.text = "Thank you for contacting Axiom LLC."


@pytest.mark.parametrize("status,chunks", [(302, []), (500, []), (200, [b"x" * (8 * 1024 * 1024 + 1)])])
def test_failed_or_oversized_download_never_reaches_ai(client, patch_genai_client, status, chunks):
    url = "https://api.twilio.com/2010-04-01/Accounts/AC" + "1" * 32 + "/Recordings/RE" + "2" * 32
    patch_genai_client.models.generate_content.reset_mock()
    with patch("requests.get") as get:
        audio = get.return_value.__enter__.return_value
        audio.status_code = status
        audio.iter_content.return_value = chunks
        response = client.post("/ai", data={"RecordingUrl": url})
    assert b"An error occurred" in response.data
    patch_genai_client.models.generate_content.assert_not_called()
