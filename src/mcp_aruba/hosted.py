"""Hosted mode: the same tools over streamable HTTP, behind the mcprush gateway.

Every call is one POST from the gateway carrying:
  - x-mcprush-token: the secret that proves the call comes from mcprush
  - X-Env-EMAIL-USER / X-Env-EMAIL-PASSWORD: the credentials of the user who
    made the call

The credentials live only for the duration of the request (a ContextVar) and
are never written to disk, logged or reused. The Aruba hosts are fixed: a
user cannot point the server at another address.

Environment:
  MCPRUSH_TOKEN          required, the token given by mcprush
  MCPRUSH_TOKEN_HEADER   default "x-mcprush-token" ("authorization" for Bearer)
  MCP_PORT               default 8770 (listens on 127.0.0.1 only)
  MCP_ALLOWED_HOSTS      public host names nginx forwards, comma separated
"""

import asyncio
import contextvars
import functools
import hmac
import json
import logging
import os
import socket
from typing import Any

from mcp.server.transport_security import TransportSecuritySettings

from .server import mcp, _request_credentials

# mcprush refuses an answer over 256 KiB, and FastMCP sends a tool result twice
# (text content and structured content): keep each result well under half.
RESULT_BUDGET = 100_000

# A preview in a list is enough to choose which email to read.
LIST_BODY_PREVIEW = 800

# mcprush gives up after 44 s; IMAP and CalDAV must answer before that.
NETWORK_TIMEOUT = 25

logger = logging.getLogger("mcp_aruba.hosted")


def _size(value: Any) -> int:
    return len(json.dumps(value, ensure_ascii=False, default=str).encode("utf-8"))


def _cut(text: str, max_bytes: int) -> str:
    """Cut a string to at most max_bytes of UTF-8, on a character boundary."""
    data = text.encode("utf-8")
    if len(data) <= max_bytes:
        return text
    return data[:max(max_bytes, 0)].decode("utf-8", errors="ignore")


def fit(result: Any, budget: int = RESULT_BUDGET) -> Any:
    """Shrink a tool result so the answer fits through the gateway.

    Lists keep their first items, with short previews, and say how many were
    left out. A single result has its long text cut and says so. An
    attachment that does not fit is refused rather than sent broken.
    """
    if _size(result) <= budget:
        return result

    if isinstance(result, dict):
        if "data_base64" in result:
            return {
                "error": "Attachment too large for the hosted version "
                         f"({result.get('size', '?')} bytes; about {budget * 3 // 8 // 1000} KB fit).",
                "filename": result.get("filename"),
                "size": result.get("size"),
            }
        out = dict(result)
        for key in ("body", "raw_content", "body_preview"):
            if isinstance(out.get(key), str):
                over = _size(out) - budget
                if over > 0:
                    keep = len(out[key].encode("utf-8")) - over - 200
                    out[key] = _cut(out[key], keep)
                    out["truncated"] = True
        if _size(out) <= budget:
            return out
        return {"error": "Result too large for the hosted version."}

    if isinstance(result, list):
        items = []
        for item in result:
            if isinstance(item, dict) and isinstance(item.get("body"), str):
                item = dict(item)
                if len(item["body"]) > LIST_BODY_PREVIEW:
                    item["body"] = item["body"][:LIST_BODY_PREVIEW]
                    item["body_truncated"] = True
            items.append(item)
        total = len(items)
        while items and _size(items) > budget - 300:
            items.pop()
        if len(items) < total:
            items.append({"note": f"{total - len(items)} more results left out to fit the answer. "
                                  "Ask for fewer, or read one email at a time."})
        return items

    return result


def _hosted_tool(fn):
    """Run a sync tool in a worker thread, with the request's credentials,
    and fit its result to the gateway limit."""

    @functools.wraps(fn)
    async def run(*args, **kwargs):
        ctx = contextvars.copy_context()
        result = await asyncio.to_thread(ctx.run, functools.partial(fn, *args, **kwargs))
        return fit(result)

    return run


def _install_tools() -> None:
    for tool in mcp._tool_manager.list_tools():
        if not getattr(tool.fn, "_hosted", False):
            tool.fn = _hosted_tool(tool.fn)
            tool.fn._hosted = True
            tool.is_async = True


def _header(headers: dict[bytes, bytes], name: str) -> str:
    raw = headers.get(name.encode("latin-1"), b"")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


class Gateway:
    """ASGI middleware: refuse calls without the mcprush token, and hold the
    caller's credentials for the duration of the request."""

    def __init__(self, app, token: str, header: str = "x-mcprush-token"):
        if not token:
            raise ValueError("MCPRUSH_TOKEN is empty")
        self.app = app
        self.token = token.encode("utf-8")
        self.header = header.lower()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = {k.lower(): v for k, v in scope["headers"]}
        given = _header(headers, self.header)
        if self.header == "authorization":
            given = given[7:] if given.lower().startswith("bearer ") else ""
        if not hmac.compare_digest(given.encode("utf-8"), self.token):
            body = b'{"error":"unauthorized"}'
            await send({"type": "http.response.start", "status": 401,
                        "headers": [(b"content-type", b"application/json"),
                                    (b"content-length", str(len(body)).encode())]})
            await send({"type": "http.response.body", "body": body})
            return

        creds = {
            "user": (_header(headers, "x-env-email-user") or _header(headers, "x-env-imap-username")).strip(),
            "password": _header(headers, "x-env-email-password") or _header(headers, "x-env-imap-password"),
        }
        reset = _request_credentials.set(creds)
        try:
            await self.app(scope, receive, send)
        finally:
            _request_credentials.reset(reset)
            creds.clear()


def build_app(token: str, header: str = "x-mcprush-token", allowed_hosts: list[str] | None = None):
    """The ASGI app nginx forwards to."""
    mcp.settings.stateless_http = True
    mcp.settings.json_response = True
    mcp.settings.streamable_http_path = "/mcp"
    hosts = [h.strip() for h in (allowed_hosts or []) if h.strip()]
    mcp.settings.transport_security = TransportSecuritySettings(
        enable_dns_rebinding_protection=bool(hosts),
        allowed_hosts=hosts + ["127.0.0.1:*", "localhost:*"],
    )
    _install_tools()
    return Gateway(mcp.streamable_http_app(), token, header)


def main():
    import uvicorn

    # Nothing about the users' mail goes to the journal: the tools log
    # recipients and subjects at INFO.
    logging.getLogger("mcp_aruba").setLevel(logging.WARNING)
    logging.getLogger("mcp").setLevel(logging.WARNING)
    socket.setdefaulttimeout(NETWORK_TIMEOUT)

    app = build_app(
        token=os.environ.get("MCPRUSH_TOKEN", ""),
        header=os.environ.get("MCPRUSH_TOKEN_HEADER", "x-mcprush-token"),
        allowed_hosts=os.environ.get("MCP_ALLOWED_HOSTS", "").split(","),
    )
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("MCP_PORT", "8770")),
                access_log=False, log_level="warning", proxy_headers=False)


if __name__ == "__main__":
    main()
