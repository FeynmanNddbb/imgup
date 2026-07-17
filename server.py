#!/usr/bin/env python3
"""
imgup - Lightweight image upload server
Auto-organizes uploads into date-based folders: YYYY-MM-DD/
"""

import os
import re
import json
import hashlib
import datetime
import email.parser
import email.policy
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/data/images")
UPLOAD_TOKEN = os.environ.get("UPLOAD_TOKEN", "change_me_please")
BASE_URL = os.environ.get("BASE_URL", "https://images.example.com")
PORT = int(os.environ.get("PORT", 8765))

ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".avif", ".ico"}
MAX_SIZE = int(os.environ.get("MAX_SIZE_MB", 20)) * 1024 * 1024  # default 20 MB


def safe_filename(name: str) -> str:
    """Sanitize filename: keep only alphanumerics, dots, dashes, underscores."""
    name = os.path.basename(name or "upload.bin")
    base, ext = os.path.splitext(name)
    ext = ext.lower()
    base = re.sub(r"[^\w\-.]", "_", base).strip("_")[:64] or "image"
    return base + ext


def parse_multipart(rfile, content_type: str, content_length: int):
    """Parse multipart/form-data without using the deprecated cgi module."""
    raw = rfile.read(min(content_length, MAX_SIZE + 1024))
    # Build a minimal email message for multipart parsing
    msg_bytes = f"Content-Type: {content_type}\r\n\r\n".encode() + raw
    parser = email.parser.BytesParser(policy=email.policy.compat32)
    msg = parser.parsebytes(msg_bytes)

    fields = {}
    for part in msg.get_payload():
        disposition = part.get("Content-Disposition", "")
        name_match = re.search(r'name="([^"]*)"', disposition)
        if not name_match:
            continue
        field_name = name_match.group(1)
        filename_match = re.search(r'filename="([^"]*)"', disposition)
        filename = filename_match.group(1) if filename_match else None
        payload = part.get_payload(decode=True)
        fields[field_name] = {"data": payload, "filename": filename}
    return fields


class UploadHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[{self.address_string()}] {fmt % args}")

    def send_json(self, code: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "X-Upload-Token, Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            self.send_json(200, {"status": "ok", "upload_dir": UPLOAD_DIR})
        else:
            self.send_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/upload":
            self.send_json(404, {"error": "not found"})
            return

        # Auth
        token = self.headers.get("X-Upload-Token", "")
        if token != UPLOAD_TOKEN:
            self.send_json(401, {"error": "unauthorized: invalid token"})
            return

        ctype = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in ctype:
            self.send_json(400, {"error": "expected multipart/form-data"})
            return

        length = int(self.headers.get("Content-Length", 0))
        if length > MAX_SIZE:
            self.send_json(413, {"error": f"file too large (max {MAX_SIZE // 1024 // 1024} MB)"})
            return

        try:
            fields = parse_multipart(self.rfile, ctype, length)
        except Exception as e:
            self.send_json(400, {"error": f"parse error: {e}"})
            return

        if "file" not in fields:
            self.send_json(400, {"error": "missing field 'file'"})
            return

        field = fields["file"]
        data: bytes = field["data"] or b""
        filename = safe_filename(field.get("filename") or "upload.bin")
        ext = os.path.splitext(filename)[1].lower()

        if ext not in ALLOWED_EXTS:
            self.send_json(400, {"error": f"unsupported type '{ext}'. allowed: {', '.join(sorted(ALLOWED_EXTS))}"})
            return

        if not data:
            self.send_json(400, {"error": "empty file"})
            return

        # Date-based directory
        today = datetime.date.today().isoformat()  # 2026-07-17
        dest_dir = os.path.join(UPLOAD_DIR, today)
        os.makedirs(dest_dir, exist_ok=True)

        # Avoid name collision: append short md5 hash
        dest_path = os.path.join(dest_dir, filename)
        if os.path.exists(dest_path):
            base, ext2 = os.path.splitext(filename)
            h = hashlib.md5(data).hexdigest()[:8]
            filename = f"{base}_{h}{ext2}"
            dest_path = os.path.join(dest_dir, filename)

        with open(dest_path, "wb") as f:
            f.write(data)

        url = f"{BASE_URL}/{today}/{filename}"
        self.send_json(200, {
            "url": url,
            "filename": filename,
            "date": today,
            "size": len(data),
        })


if __name__ == "__main__":
    print(f"imgup server  v1.0")
    print(f"  Listening : 127.0.0.1:{PORT}")
    print(f"  Upload dir: {UPLOAD_DIR}")
    print(f"  Base URL  : {BASE_URL}")
    print(f"  Max size  : {MAX_SIZE // 1024 // 1024} MB")
    server = HTTPServer(("127.0.0.1", PORT), UploadHandler)
    server.serve_forever()
