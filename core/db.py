"""
Database helper. CivicLens stores everything in one SQLite file (civiclens.db),
so you don't need to install or set up any database server.
"""
import sqlite3
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DB_PATH = BASE / "civiclens.db"
PHOTO_DIR = BASE / "photos"
PHOTO_DIR.mkdir(exist_ok=True)


def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row   # lets us read columns by name: row["category"]
    return con


def init_db():
    """Create the tables the first time the app runs."""
    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS issues (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                category      TEXT,
                department    TEXT,
                latitude      REAL,
                longitude     REAL,
                description   TEXT,
                photo         TEXT,
                after_photo   TEXT,
                report_count  INTEGER DEFAULT 1,
                severity      INTEGER,
                status        TEXT DEFAULT 'Open',      -- Open / In progress / Resolved
                escalated     INTEGER DEFAULT 0,        -- 0 = no, 1 = yes
                ai_confidence REAL,
                created_at    TEXT,
                resolved_at   TEXT
            )""")
        con.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                issue_id  INTEGER,
                photo     TEXT,
                created_at TEXT
            )""")


def now():
    return datetime.now().isoformat(timespec="seconds")


def save_photo(image_bytes, prefix="report"):
    """Save an uploaded photo to the photos folder and return its file path."""
    name = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
    path = PHOTO_DIR / name
    path.write_bytes(image_bytes)
    return str(path)


def all_issues():
    with connect() as con:
        return [dict(r) for r in con.execute("SELECT * FROM issues ORDER BY id DESC")]


def get_issue(issue_id):
    with connect() as con:
        r = con.execute("SELECT * FROM issues WHERE id = ?", (issue_id,)).fetchone()
        return dict(r) if r else None


def add_issue(category, department, lat, lon, description, photo, severity, confidence):
    with connect() as con:
        cur = con.execute(
            """INSERT INTO issues (category, department, latitude, longitude, description,
                                   photo, severity, ai_confidence, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (category, department, lat, lon, description, photo, severity, confidence, now()))
        issue_id = cur.lastrowid
        con.execute("INSERT INTO reports (issue_id, photo, created_at) VALUES (?, ?, ?)",
                    (issue_id, photo, now()))
        return issue_id


def add_duplicate_report(issue_id, photo):
    """Someone reported an issue that already exists: count it, don't create a new one."""
    with connect() as con:
        con.execute("UPDATE issues SET report_count = report_count + 1 WHERE id = ?", (issue_id,))
        con.execute("INSERT INTO reports (issue_id, photo, created_at) VALUES (?, ?, ?)",
                    (issue_id, photo, now()))


def update_issue(issue_id, **fields):
    """Update any columns, e.g. update_issue(3, status='Resolved')."""
    if not fields:
        return
    cols = ", ".join(f"{k} = ?" for k in fields)
    with connect() as con:
        con.execute(f"UPDATE issues SET {cols} WHERE id = ?", (*fields.values(), issue_id))
