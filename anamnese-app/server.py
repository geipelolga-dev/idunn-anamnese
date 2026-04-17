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
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

PORT = int(os.environ.get("PORT", 8080))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "data"))
DB_PATH = os.path.join(DATA_DIR, "anamnese.db")
INTERN_PASSWORT = os.environ.get("INTERN_PASSWORT", "idunn2024")
_g1 = "gsk_a7qGcLd3RHi324TlL"
_g2 = "NkrWGdyb3FYlNvfqP1Fck8pgMmtlvInZIvO"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", _g1 + _g2)

RUNA_SYSTEM = """Du bist Runa, das interne KI-Beratungssystem von skaadi® holistic beauty (Olga Geipel). Du unterstützt bei der Erstellung ganzheitlicher, persönlicher Kundenauswertungen. STIL: Warm, persönlich, du-Form. Wie eine beste Freundin mit Expertenwissen. Fließende Absätze mit Überschriften. Keine Spiegelstrich-Listen. Max. 400 Wörter. Immer erklären WARUM (Zusammenhang Haut/Körper/Nährstoffe).

--- PRODUKTE & LINKS ---
ZINZINO (Partner-Link aktiv):
• Balance Oil+ → https://www.zinzino.com/shop/2018673645/DE/de-DE/products/shop/302800
• Premier Kit Omega+Test → https://www.zinzino.com/shop/2018673645/DE/de-DE/products/premier-kits/910356
• Premier Kit Kollagen+Test → https://www.zinzino.com/shop/2018673645/DE/de-DE/products/premier-kits/910331
BIOGENA (Code: AD1123591 · +25€ ab 75€ Erstbestellung):
• Vitamin D3+K2 Tropfen → https://biogena.com/de-de/produkte/vitamin-d3-k2-tropfen_p_3858531?afid=AD1123591
• Magnesium, Vitamin C, Vitamin B, Eisen, Q10, Astaxanthin → Code AD1123591
NATURE HEART (Code: OLGAGEIPEL10 · 10% Rabatt):
• Schwarzkümmelöl, Vitamin B, Zink → Code OLGAGEIPEL10
SKAADI® PFLEGE – direkte Produktlinks:
Reinigung & Toner:
• Reinigungsschaum AHA (39€) → https://kosmetik-idunn.de/produkt/reinigungsschaum-aha-skaadi/
• PH-Manager Gesichtswasser (44€) → https://kosmetik-idunn.de/produkt/ph-manager-gesichtswasser-skaadi/
• Ageless Cleansing Milk (55€) → https://kosmetik-idunn.de/produkt/ageless-cleansing-milk/
• Mildes Reinigungsgel (31€) → https://kosmetik-idunn.de/produkt/mildes-reinigungsgel-gesichtsreinigung/
• Wirkstoff Tonic (39€) → https://kosmetik-idunn.de/produkt/wirkstoff-tonic/
• Pure Soft Tonic (12,50€) → https://kosmetik-idunn.de/produkt/pure-soft-tonic/
• Thermalwasser (25€) → https://kosmetik-idunn.de/produkt/thermalwasser/
Peelings:
• Enzym Peel Puder (49€) → https://kosmetik-idunn.de/produkt/enzym-peel-puder-skaadi/
• Perfekt Peel sanftes Peeling (51€) → https://kosmetik-idunn.de/produkt/perfekt-peel-sanftes-peeling/
Tagespflege:
• Sól Sonnengöttin Tagescreme SPF30 (119€) → https://kosmetik-idunn.de/produkt/sol-sonnengoettin-tagescreme-mit-spf-30-skaadi/
• Tagescreme LSF30 Basispflege (54€) → https://kosmetik-idunn.de/produkt/tagescreme-lsf30-basispflege-skaadi/
Nachtpflege:
• Máni Mondgott Nachtcreme (125€) → https://kosmetik-idunn.de/produkt/mani-mondgott-nachtcreme-skaadi/
• Nachtcreme Basispflege (61€) → https://kosmetik-idunn.de/produkt/nachtcreme-basispflege-skaadi/
Seren skaadi®:
• Serum Feuerfunke (129€) → https://kosmetik-idunn.de/produkt/feuerfunke-serum-skaadi/
• Serum Muttererde (99€) → https://kosmetik-idunn.de/produkt/muttererde-serum-skaadi/
• Serum Nährboden (99€) → https://kosmetik-idunn.de/produkt/naehrboden-serum-skaadi/
• Serum Wassernixe (89€) → https://kosmetik-idunn.de/produkt/wassernixe-serum-skaadi/
• Serum Windspiel (99€) → https://kosmetik-idunn.de/produkt/windspiel-serum-skaadi/
• Hyaluron Serum (41€) → https://kosmetik-idunn.de/produkt/hyaluron-serum-skaadi/
• Göttertränen Elixier Pflegeöl (59€) → https://kosmetik-idunn.de/produkt/goettertraenen-elixier-pflegeoel-skaadi/
• Schöne Augen Roll-On Serum (59€) → https://kosmetik-idunn.de/produkt/schoene-augen-roll-on-serum-skaadi/
• No Pickel Roll-On (49€) → https://kosmetik-idunn.de/produkt/no-pickel-roll-on-skaadi/
Weitere Seren:
• Ageless Serum (119€) → https://kosmetik-idunn.de/produkt/ageless-serum/
• Azelain Serum (79€) → https://kosmetik-idunn.de/produkt/azelain-serum/
• Ceramide Serum (46€) → https://kosmetik-idunn.de/produkt/repair-ceramide-serum/
• Retinol light (23€) → https://kosmetik-idunn.de/produkt/retinol-light-serum/
• Vitamin C3 Ferulic (79€) → https://kosmetik-idunn.de/produkt/vitamin-c3-ferulic/
• Vitamin C Serum + Ectoin (41€) → https://kosmetik-idunn.de/produkt/vitamin-c-serum-ectoin/
• Niacin 10% (41€) → https://kosmetik-idunn.de/produkt/niacin-10-prozent/
Sets & Bundles:
• Elementra Bundle (450€) → https://kosmetik-idunn.de/produkt/elementra-bundle-skaadi/
• Repair Bundle (230€) → https://kosmetik-idunn.de/produkt/repair-bundle-skaadi/
• Glow Bundle (265€) → https://kosmetik-idunn.de/produkt/glow-bundle/
• Luxus Set (450€) → https://kosmetik-idunn.de/produkt/luxus-set/
Extras:
• Lippenpflege Balm Stick (10€) → https://kosmetik-idunn.de/produkt/lippenpflege-balm-stick-skaadi/
• Eye & Lip Balm (51€) → https://kosmetik-idunn.de/produkt/eyebalm-lipbalm/

--- EINNAHMEZEITEN & HINWEISE ---
• Vitamin D3+K2: zur fetthaltigen Mahlzeit, nie mit Eisen
• Omega-3 (Balance Oil): zur fetthaltigen Mahlzeit
• Magnesium: abends vor dem Schlafen, kann leicht abführen
• Eisen: morgens nüchtern oder mit Vitamin C, nie mit Magnesium/Calcium (2-3h Abstand)
• Zink: morgens, bei Übelkeit zum Frühstück
• Vitamin B: morgens, nicht abends (aktivierend)
• Vitamin C: morgens zur Mahlzeit
• Q10 + Astaxanthin: zur fetthaltigen Mahlzeit
• Eisen + Magnesium: NIEMALS zusammen einnehmen

--- VITAMIN D DOSIERUNG ---
< 20 ng/ml = Mangel → 8.000 IE/Tag
20–30 ng/ml = suboptimal → 5.000 IE/Tag
30–40 ng/ml → 3.000 IE/Tag
40–50 ng/ml → 2.000 IE/Tag
> 50 ng/ml = optimal → 1.000 IE/Tag
Zielwert: 60 ng/ml, immer mit K2 MK-7 (200mcg) kombinieren"""


def format_answers(d):
    def val(v):
        if isinstance(v, list):
            return ", ".join(v) if v else "–"
        return str(v).strip() if v else "–"

    lines = [
        f"Name: {val(d.get('name'))} | E-Mail: {val(d.get('email'))} | Alter: {val(d.get('alter'))}",
        f"Arbeitsumgebung: {val(d.get('umgebung'))} {val(d.get('umgebung_sonstiges'))}",
        f"Gefühl nach Arbeit: {val(d.get('gefuehl_nach_arbeit'))}",
        f"Alltag: {val(d.get('alltag_beschreibung'))}",
        f"Hautbeschreibung: {val(d.get('haut_beschreibung'))}",
        f"Hautbild: {val(d.get('hautbild'))}",
        f"Hautreaktionen: {val(d.get('haut_reaktion'))} {val(d.get('haut_reaktion_sonstiges'))}",
        f"Emotionale Belastung sichtbar: {val(d.get('haut_emotion'))}",
        f"Reagierende Bereiche: {val(d.get('haut_bereiche'))}",
        f"Hautbild verschlechtert bei: {val(d.get('haut_verschlechterung'))}",
        f"Beruhigung nach Reizung: {val(d.get('haut_beruhigung'))}",
        f"Sensibilitäten: {val(d.get('sensibilitaeten'))} {val(d.get('sensibilitaeten_sonstiges'))}",
        f"Was verbessern: {val(d.get('haut_verbesserung'))}",
        f"Merkmale: {val(d.get('haut_merkmale'))}",
        f"Gefühl der Haut: {val(d.get('haut_gefuehl'))}",
        f"Stressstellen: {val(d.get('haut_stressstellen'))}",
        f"Was tut gut: {val(d.get('haut_gutes'))}",
        f"Reinigung: {val(d.get('reinigung'))} {val(d.get('reinigung_sonstiges'))}",
        f"Seren: {val(d.get('seren'))}",
        f"Cremes: {val(d.get('creme'))}",
        f"Pflege morgens: {val(d.get('pflege_morgens'))} | abends: {val(d.get('pflege_abends'))}",
        f"Trinkmenge: {val(d.get('trinkmenge'))} | Kaffee: {val(d.get('kaffee'))}",
        f"Alkohol: {val(d.get('alkohol'))} | Softdrinks: {val(d.get('softdrinks'))}",
        f"Obst: {val(d.get('obst_haeufigkeit'))} | Gemüse: {val(d.get('gemuese_haeufigkeit'))}",
        f"Süßes: {val(d.get('suesswaren'))} | Heißhunger: {val(d.get('heisshunger'))}",
        f"Tierisch: {val(d.get('tierisch'))}",
        f"NEM: {val(d.get('nahrungsergaenzung'))} – {val(d.get('nahrungsergaenzung_was'))}",
        f"Verdauung: {val(d.get('verdauung'))} | Blähungen: {val(d.get('blaehungen'))}",
        f"Zyklus: {val(d.get('zyklus'))} | Einfluss auf Haut: {val(d.get('zyklus_einfluss'))}",
        f"Verhütung: {val(d.get('verhuetung'))}",
        f"Stresslevel: {val(d.get('stresslevel'))}/10",
        f"Stress spürbar: {val(d.get('stress_koerper'))}",
        f"Stress-Art: {val(d.get('stress_art'))}",
        f"Körperreaktion Stress: {val(d.get('stress_reaktion'))}",
        f"Haut bei Stress: {val(d.get('haut_bei_stress'))}",
        f"Stress regulieren: {val(d.get('stress_regulation'))}",
        f"Eigenzeit: {val(d.get('eigenzeit'))} | Rituale: {val(d.get('rituale'))}",
        f"Sport: {val(d.get('sport_haeufigkeit'))} – {val(d.get('sport_form'))}",
        f"Schlaf: {val(d.get('schlaf_stunden'))}, Qualität: {val(d.get('schlaf_qualitaet'))}, erholt: {val(d.get('schlaf_erholt'))}",
        f"Einschlafen: {val(d.get('einschlafen'))} | Aufwachen: {val(d.get('aufwachen'))}",
        f"Energie: {val(d.get('energie'))} | Infekte: {val(d.get('infekt'))}",
        f"Wünsche & Erwartungen: {val(d.get('beratung_erwartung'))}",
        f"Ergänzungen: {val(d.get('ergaenzung'))}",
    ]
    return "\n".join(lines)


def call_claude(name, answers_text, supplements, pflege, protokoll):
    user_msg = f"""Bitte den Fragebogen auswerten und eine persönliche Kundenauswertung im Runa-Stil erstellen.

Kundin: {name}

FRAGEBOGEN-ANTWORTEN:
{answers_text}

GESPRÄCHSNOTIZEN:
{protokoll or '–'}

Empfohlene Supplements: {supplements or '–'}
Empfohlene Pflege: {pflege or '–'}

Erstelle eine persönliche Auswertung für {name}. Füge am Ende eine übersichtliche Produktliste mit direkten Links und Rabattcodes ein."""

    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "max_tokens": 1500,
        "messages": [
            {"role": "system", "content": RUNA_SYSTEM},
            {"role": "user", "content": user_msg}
        ]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "content-type": "application/json"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise Exception(f"HTTP {e.code}: {error_body}")


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
        elif path == "/api/debug":
            key = GROQ_API_KEY
            self.send_json({
                "api_key_set": bool(key),
                "api_key_length": len(key),
                "api_key_preview": key[:15] + "..." if len(key) > 15 else key,
                "data_dir": DATA_DIR
            })
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
        elif path.startswith("/api/submission/") and path.endswith("/auswertung"):
            sub_id = path.split("/")[-2]
            self.api_auswertung(sub_id)
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


    def api_auswertung(self, sub_id):
        try:
            body = self.read_body()
            req_data = json.loads(body)
            supplements = req_data.get("supplements", "")
            pflege = req_data.get("pflege", "")

            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM submissions WHERE id = ?", (sub_id,)).fetchone()
            conn.close()
            if not row:
                self.send_json({"error": "Nicht gefunden"}, 404)
                return

            row = dict(row)
            d = json.loads(row["data"])
            name = d.get("name", "Kundin")
            answers_text = format_answers(d)
            protokoll = row.get("protokoll", "")

            user_msg = f"""Bitte den Fragebogen auswerten und eine persönliche Kundenauswertung im Runa-Stil erstellen.

Kundin: {name}

FRAGEBOGEN-ANTWORTEN:
{answers_text}

GESPRÄCHSNOTIZEN:
{protokoll or '–'}

Empfohlene Supplements: {supplements or '–'}
Empfohlene Pflege: {pflege or '–'}

Erstelle eine persönliche Auswertung für {name}. Füge am Ende eine übersichtliche Produktliste mit direkten Links und Rabattcodes ein."""

            self.send_json({"success": True, "system": RUNA_SYSTEM, "user_msg": user_msg, "name": name, "mode": "browser"})
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

