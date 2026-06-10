#!/usr/bin/env python3
"""Basic-auth HTTP proxy for viewing local Paperclip through Tailscale Funnel.

Security model:
- Public internet hits this proxy, not Paperclip directly.
- Proxy requires HTTP Basic Auth.
- Proxy rewrites Host/Origin to localhost so Paperclip's private host checks pass.
- Credentials are supplied by env vars, not committed.
"""
from __future__ import annotations

import base64
import hmac
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

LISTEN_HOST = os.environ.get("PAPERCLIP_PROXY_HOST", "127.0.0.1")
LISTEN_PORT = int(os.environ.get("PAPERCLIP_PROXY_PORT", "3110"))
TARGET = os.environ.get("PAPERCLIP_TARGET", "http://127.0.0.1:3100")
USERNAME = os.environ.get("PAPERCLIP_PROXY_USER", "stefan")
PASSWORD = os.environ.get("PAPERCLIP_PROXY_PASS")

HOP_BY_HOP = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade",
}

if not PASSWORD:
    raise SystemExit("PAPERCLIP_PROXY_PASS is required")

EXPECTED = "Basic " + base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()

class Proxy(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self): self.forward()
    def do_POST(self): self.forward()
    def do_PUT(self): self.forward()
    def do_PATCH(self): self.forward()
    def do_DELETE(self): self.forward()
    def do_OPTIONS(self): self.forward()

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)

    def unauthorized(self):
        data = b"Authentication required\n"
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Paperclip"')
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def forward(self):
        auth = self.headers.get("Authorization", "")
        if not hmac.compare_digest(auth, EXPECTED):
            return self.unauthorized()

        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length) if length else None
        headers = {k: v for k, v in self.headers.items() if k.lower() not in HOP_BY_HOP and k.lower() != "authorization"}
        headers["Host"] = "localhost:3100"
        headers.pop("X-Forwarded-Host", None)
        headers.pop("X-Forwarded-Proto", None)
        headers.pop("Forwarded", None)
        if "Origin" in headers:
            headers["Origin"] = "http://localhost:3100"
        if "Referer" in headers:
            headers["Referer"] = "http://localhost:3100/"

        try:
            resp = requests.request(
                self.command,
                TARGET + self.path,
                headers=headers,
                data=body,
                stream=True,
                timeout=60,
                allow_redirects=False,
            )
            content = resp.content
            self.send_response(resp.status_code)
            for k, v in resp.headers.items():
                if k.lower() in HOP_BY_HOP or k.lower() in {"content-encoding", "content-length"}:
                    continue
                self.send_header(k, v)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            data = f"Proxy error: {e}\n".encode()
            self.send_response(502)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

if __name__ == "__main__":
    server = ThreadingHTTPServer((LISTEN_HOST, LISTEN_PORT), Proxy)
    print(f"Paperclip public auth proxy on http://{LISTEN_HOST}:{LISTEN_PORT} -> {TARGET} as user {USERNAME}", flush=True)
    server.serve_forever()
