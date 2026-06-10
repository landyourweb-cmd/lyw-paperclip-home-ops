#!/usr/bin/env python3
"""HTTP reverse proxy: expose local Paperclip on Tailscale and rewrite Host to localhost."""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import requests

LISTEN_HOST = "100.87.124.37"
LISTEN_PORT = 3101
TARGET = "http://127.0.0.1:3100"

HOP_BY_HOP = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade",
}

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

    def forward(self):
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length) if length else None
        headers = {k: v for k, v in self.headers.items() if k.lower() not in HOP_BY_HOP}
        headers["Host"] = "localhost:3100"
        headers.pop("X-Forwarded-Host", None)
        headers.pop("X-Forwarded-Proto", None)
        headers.pop("Forwarded", None)
        headers["Origin"] = "http://localhost:3100" if "Origin" in headers else headers.get("Origin", "")
        if not headers["Origin"]:
            headers.pop("Origin", None)
        url = TARGET + self.path
        try:
            resp = requests.request(self.command, url, headers=headers, data=body, stream=True, timeout=60, allow_redirects=False)
            content = resp.content
            self.send_response(resp.status_code)
            for k, v in resp.headers.items():
                if k.lower() in HOP_BY_HOP or k.lower() == "content-encoding":
                    continue
                if k.lower() == "content-length":
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
    print(f"Paperclip HTTP proxy listening on http://{LISTEN_HOST}:{LISTEN_PORT} -> {TARGET}", flush=True)
    server.serve_forever()
