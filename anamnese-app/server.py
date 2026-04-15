#!/usr/bin/env python3
"""
Idunn Anamnese App - Server
Starten: python3 server.py
Dann im Browser öffnen: http://localhost:8080
"""

import http.server
import socketserver
import json
import sqlite3
import os
import urllib.parse
from datetime import datetime

PORT = int(os.environ.get("PORT", 8080))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "data"))
DB_PATH = os.path.join(DATA_DIR, "anamnese.db")
INTERN_PASSWORT = os.environ.get("INTERN_PASSWORT", "idunn2024")


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            email TEXT,
            name TEXT,
            data TEXT,
            protokoll TEXT DEFAULT '',
            protokoll_updated_at TEXT
        )
    """)
    conn.commit()
    conn.close()


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def log_message(self, format, *args):
        pass  # Weniger Ausgabe in der Konsole

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/fragebogen":
            self.serve_file("fragebogen.html")
        elif path == "/intern":
            self.serve_file("intern.html")
        elif path == "/api/submissions":
            self.api_get_submissions()
        elif path.startswith("/api/submission/"):
            sub_id = path.split("/")[-1]
            self.api_get_submission(sub_id)
        elif path == "/api/check":
            self.send_json({"status": "ok"})
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/submit":
            self.api_submit()
        elif path.startswith("/api/submission/") and path.endswith("/protokoll"):
            sub_id = path.split("/")[-2]
            self.api_save_protokoll(sub_id)
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def serve_file(self, filename):
        filepath = os.path.join(BASE_DIR, filename)
        if not os.path.exists(filepath):
            self.send_error(404, f"Datei nicht gefunden: {filename}")
            return
        with open(filepath, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(content))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length)

    def api_submit(self):
        try:
            body = self.read_body()
            data = json.loads(body)
            email = data.get("email", "")
            name = data.get("name", "")
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.execute(
                "INSERT INTO submissions (email, name, data) VALUES (?, ?, ?)",
                (email, name, json.dumps(data, ensure_ascii=False))
            )
            sub_id = cursor.lastrowid
            conn.commit()
            conn.close()
            self.send_json({"success": True, "id": sub_id})
        except Exception as e:
            self.send_json({"success": False, "error": str(e)}, 500)

    def api_get_submissions(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT id, created_at, email, name, protokoll FROM submissions ORDER BY created_at DESC"
            ).fetchall()
            conn.close()
            result = [dict(r) for r in rows]
            self.send_json(result)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    def api_get_submission(self, sub_id):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM submissions WHERE id = ?", (sub_id,)
            ).fetchone()
            conn.close()
            if not row:
                self.send_json({"error": "Nicht gefunden"}, 404)
                return
            result = dict(row)
            result["data"] = json.loads(result["data"])
            self.send_json(result)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    def api_save_protokoll(self, sub_id):
        try:
            body = self.read_body()
            data = json.loads(body)
            protokoll = data.get("protokoll", "")
            now = datetime.now().strftime("%d.%m.%Y %H:%M")
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "UPDATE submissions SET protokoll = ?, protokoll_updated_at = ? WHERE id = ?",
                (protokoll, now, sub_id)
            )
            conn.commit()
            conn.close()
            self.send_json({"success": True})
        except Exception as e:
            self.send_json({"success": False, "error": str(e)}, 500)


if __name__ == "__main__":
    init_db()
    print("=" * 55)
    print("  Idunn Anamnese App läuft!")
    print("=" * 55)
    print(f"\n  Fragebogen-Link für Kunden:")
    print(f"  http://localhost:{PORT}/fragebogen")
    print(f"\n  Interner Bereich:")
    print(f"  http://localhost:{PORT}/intern")
    print(f"  Passwort: {INTERN_PASSWORT}")
    print("\n  Zum Beenden: Ctrl+C drücken")
    print("=" * 55)
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        httpd.allow_reuse_address = True
        httpd.serve_forever()
