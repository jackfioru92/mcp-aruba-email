"""Attachment enumeration and download.

Regression test: ``get_email_attachments`` used to return the absolute MIME
part index while ``download_attachment`` expected an attachment-relative one,
and ``message/rfc822`` parts (e.g. the ``postacert.eml`` inside a PEC message)
could not be downloaded at all. Both now share ``_iter_attachments``.
"""

import base64
from email.message import EmailMessage

import pytest

from mcp_aruba.email_client import ArubaEmailClient


class _FakeConn:
    """Minimal IMAP connection stub returning a fixed raw message."""

    def __init__(self, raw: bytes):
        self.raw = raw

    def select(self, folder):
        return ("OK", [b"1"])

    def fetch(self, message_id, spec):
        return ("OK", [(b"1 (RFC822)", self.raw)])


def _build_pec_message() -> bytes:
    """A PEC-like message: a data attachment + an embedded message/rfc822."""
    inner = EmailMessage()
    inner["Subject"] = "risposta"
    inner["From"] = "ente@pec.it"
    inner["To"] = "dataciviclab@pec.it"
    inner.set_content("contenuto reale della risposta")

    outer = EmailMessage()
    outer["Subject"] = "POSTA CERTIFICATA: risposta"
    outer["From"] = "posta-certificata@pec.aruba.it"
    outer["To"] = "dataciviclab@pec.it"
    outer.set_content("wrapper PEC")
    outer.add_attachment(
        b"<xml/>", maintype="application", subtype="xml", filename="daticert.xml"
    )
    outer.add_attachment(inner, filename="postacert.eml")
    return outer.as_bytes()


def _client(raw: bytes) -> ArubaEmailClient:
    client = ArubaEmailClient("imaps.pec.aruba.it", 993, "u", "p")
    client._connection = _FakeConn(raw)
    return client


def test_indices_are_attachment_relative():
    """The index from get_email_attachments is valid for download_attachment."""
    client = _client(_build_pec_message())
    attachments = client.get_email_attachments("1")

    assert [a["index"] for a in attachments] == [0, 1]
    assert [a["filename"] for a in attachments] == ["daticert.xml", "postacert.eml"]


def test_message_rfc822_has_nonzero_size():
    """A message/rfc822 part must report its real size, not 0."""
    client = _client(_build_pec_message())
    attachments = {a["filename"]: a for a in client.get_email_attachments("1")}
    assert attachments["postacert.eml"]["size"] > 0


def test_download_regular_attachment():
    client = _client(_build_pec_message())
    att = client.download_attachment("1", 0)
    assert att["filename"] == "daticert.xml"
    assert base64.b64decode(att["data_base64"]) == b"<xml/>"


def test_download_embedded_message():
    """The embedded postacert.eml is downloadable and carries the real body."""
    client = _client(_build_pec_message())
    att = client.download_attachment("1", 1)
    assert att["filename"] == "postacert.eml"
    payload = base64.b64decode(att["data_base64"])
    assert b"contenuto reale della risposta" in payload


def test_download_out_of_range_raises():
    client = _client(_build_pec_message())
    with pytest.raises(Exception, match="not found"):
        client.download_attachment("1", 5)
