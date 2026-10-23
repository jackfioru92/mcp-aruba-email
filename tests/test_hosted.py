"""Hosted mode: token check, per-request credentials, fixed hosts, answer size.

No network: the IMAP and CalDAV clients are replaced by fakes that record
what they were built with.
"""

import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from starlette.testclient import TestClient

import mcp_aruba.server as server
from mcp_aruba import hosted

TOKEN = "mgw_test_token_123"
HOST = "edge.example.it"


class FakeEmailClient:
    built = []

    def __init__(self, host, port, username, password, smtp_host=None, smtp_port=465):
        self.args = dict(host=host, port=port, username=username, password=password, smtp_host=smtp_host)
        FakeEmailClient.built.append(self.args)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def list_emails(self, folder="INBOX", sender_filter=None, limit=10):
        # Slow enough that two concurrent calls overlap.
        time.sleep(0.2)
        return [{"id": "1", "from": self.args["username"], "subject": "hi", "body": "x" * 5000}] * limit

    def read_email(self, email_id, folder="INBOX"):
        return {"id": email_id, "subject": "big", "body": "è" * 150_000}

    def download_attachment(self, email_id, attachment_index, folder="INBOX"):
        return {"filename": "a.pdf", "content_type": "application/pdf", "size": 300_000, "data_base64": "A" * 400_000}

    def send_email(self, **kwargs):
        FakeEmailClient.sent = kwargs
        return {"status": "sent"}


class FakeCalendarClient:
    built = []

    def __init__(self, url, username, password):
        FakeCalendarClient.built.append(dict(url=url, username=username, password=password))

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def list_events(self, start_date=None, end_date=None, limit=50):
        return []

    def create_event(self, **kwargs):
        return {"success": True, "summary": kwargs["summary"]}


@pytest.fixture(scope="module")
def client():
    mp = pytest.MonkeyPatch()
    mp.setattr(server, "ArubaEmailClient", FakeEmailClient)
    mp.setattr(server, "ArubaCalendarClient", FakeCalendarClient)
    # Credentials of the server's owner must never be used for a hosted call.
    mp.setitem(server.IMAP_CONFIG, "username", "owner@server.it")
    mp.setitem(server.IMAP_CONFIG, "password", "owner-secret")
    app = hosted.build_app(TOKEN, allowed_hosts=[HOST])
    with TestClient(app, base_url=f"https://{HOST}") as c:
        yield c
    mp.undo()


def call(client, tool, args=None, token=TOKEN, user="mario@ditta.it", password="pw-mario", extra=None, host=HOST):
    headers = {"accept": "application/json, text/event-stream", "content-type": "application/json", "host": host}
    if token is not None:
        headers["x-mcprush-token"] = token
    if user is not None:
        headers["x-env-email-user"] = user
    if password is not None:
        headers["x-env-email-password"] = password
    headers.update(extra or {})
    body = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": tool, "arguments": args or {}}}
    return client.post("/mcp", json=body, headers=headers)


def result_of(resp):
    assert resp.status_code == 200, resp.text
    structured = resp.json()["result"]["structuredContent"]
    # A tool returning a list is wrapped as {"result": [...]}.
    return structured["result"] if set(structured) == {"result"} else structured


# --- the token ------------------------------------------------------------

def test_without_token_is_refused(client):
    assert call(client, "list_emails", token=None).status_code == 401


def test_with_a_wrong_token_is_refused(client):
    assert call(client, "list_emails", token="mgw_test_token_12X").status_code == 401


def test_the_token_is_compared_whole_not_by_prefix(client):
    assert call(client, "list_emails", token=TOKEN + "extra").status_code == 401


def test_tools_list_without_token_is_refused(client):
    resp = client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                       headers={"accept": "application/json, text/event-stream"})
    assert resp.status_code == 401


def test_tools_list_with_token_declares_the_tools(client):
    resp = client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                       headers={"accept": "application/json, text/event-stream", "x-mcprush-token": TOKEN})
    names = {t["name"] for t in resp.json()["result"]["tools"]}
    assert {"list_emails", "read_email", "send_email", "list_calendar_events"} <= names


def test_an_unknown_host_header_is_refused(client):
    assert call(client, "list_emails", host="evil.example.com").status_code in (400, 421)


# --- credentials ------------------------------------------------------------

def test_credentials_come_from_the_headers_and_hosts_are_fixed(client):
    FakeEmailClient.built.clear()
    out = result_of(call(client, "list_emails", {"limit": 1},
                         extra={"x-env-imap-host": "10.0.0.5", "x-env-smtp-host": "evil.example.com"}))
    assert out[0]["from"] == "mario@ditta.it"
    built = FakeEmailClient.built[-1]
    assert built["host"] == "imaps.aruba.it" and built["smtp_host"] == "smtps.aruba.it"
    assert built["password"] == "pw-mario"


def test_calendar_url_is_built_from_the_user(client):
    FakeCalendarClient.built.clear()
    result_of(call(client, "list_calendar_events", extra={"x-env-caldav-url": "http://169.254.169.254/"}))
    assert FakeCalendarClient.built[-1]["url"] == "https://syncdav.aruba.it/calendars/mario@ditta.it/"


def test_calendar_events_can_be_created(client):
    out = result_of(call(client, "create_calendar_event",
                         {"summary": "Riunione", "start": "2026-11-02T10:00:00", "end": "2026-11-02T11:00:00"}))
    assert out == {"success": True, "summary": "Riunione"}


def test_missing_credentials_never_fall_back_to_the_server_owner(client):
    FakeEmailClient.built.clear()
    out = result_of(call(client, "list_emails", user=None, password=None))
    assert "credentials missing" in json.dumps(out)
    assert FakeEmailClient.built == []


def test_concurrent_calls_keep_their_own_credentials(client):
    def one(i):
        out = result_of(call(client, "list_emails", {"limit": 1}, user=f"user{i}@x.it", password=f"pw{i}"))
        return out[0]["from"]

    with ThreadPoolExecutor(max_workers=6) as pool:
        got = list(pool.map(one, range(6)))
    assert got == [f"user{i}@x.it" for i in range(6)]


def test_credentials_do_not_outlive_the_request(client):
    result_of(call(client, "list_emails", {"limit": 1}))
    assert server._request_credentials.get() is None


# --- what reads or writes the server's files --------------------------------

@pytest.mark.parametrize("tool,args", [
    ("save_attachment", {"email_id": "1", "attachment_index": 0}),
    ("set_email_signature", {"name": "Mario", "email": "mario@ditta.it"}),
    ("get_email_signature", {}),
    ("list_email_signatures", {}),
])
def test_file_tools_are_off(client, tool, args):
    out = result_of(call(client, tool, args))
    assert "not available in the hosted version" in json.dumps(out)


def test_sending_with_a_local_attachment_is_refused(client):
    out = result_of(call(client, "send_email", {"to": "a@b.it", "subject": "s", "body": "b",
                                                 "attachments": "/etc/passwd"}))
    assert "not available in the hosted version" in json.dumps(out)


def test_sending_uses_no_server_signature(client):
    FakeEmailClient.sent = None
    result_of(call(client, "send_email", {"to": "a@b.it", "subject": "s", "body": "b"}))
    assert FakeEmailClient.sent["use_signature"] is False


# --- answer size --------------------------------------------------------------

def test_a_long_list_fits_through_the_gateway(client):
    resp = call(client, "list_emails", {"limit": 50})
    assert len(resp.content) < 256 * 1024
    out = result_of(resp)
    assert out[0]["body_truncated"] is True


def test_a_long_email_is_cut_and_says_so(client):
    resp = call(client, "read_email", {"email_id": "1"})
    assert len(resp.content) < 256 * 1024
    out = result_of(resp)
    assert out["truncated"] is True and out["body"].startswith("è")


def test_a_big_attachment_is_refused_not_broken(client):
    out = result_of(call(client, "download_attachment", {"email_id": "1", "attachment_index": 0}))
    assert "too large" in out["error"] and "data_base64" not in out


def test_fit_leaves_small_results_alone():
    assert hosted.fit({"body": "ciao"}) == {"body": "ciao"}
    assert hosted.fit([{"id": "1"}]) == [{"id": "1"}]


def test_fit_says_how_many_items_were_left_out():
    out = hosted.fit([{"id": str(i), "body": "y" * 700} for i in range(500)], budget=50_000)
    assert "more results left out" in out[-1]["note"]
    assert hosted._size(out) <= 50_000


def test_cut_never_splits_a_character():
    assert hosted._cut("èèè", 3) == "è"


def test_local_calendar_url_defaults_to_the_user(monkeypatch):
    import importlib
    monkeypatch.delenv("CALDAV_URL", raising=False)
    monkeypatch.delenv("IMAP_USERNAME", raising=False)
    monkeypatch.setenv("EMAIL_USER", "anna@studio.it")
    monkeypatch.setenv("EMAIL_PASSWORD", "pw")
    fresh = importlib.reload(server)
    try:
        assert fresh.CALDAV_CONFIG["url"] == "https://syncdav.aruba.it/calendars/anna@studio.it/"
        assert fresh.IMAP_CONFIG["username"] == "anna@studio.it"
    finally:
        monkeypatch.undo()
        importlib.reload(server)
