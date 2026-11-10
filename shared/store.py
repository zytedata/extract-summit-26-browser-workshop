"""One small SQLite database that every agent writes to as it goes.

The dashboard (lesson 06) reads it every couple of seconds, so you see the
agents work while they run. Every run adds rows, nothing is replaced, so
running it again next week gives you history.

Four tables:
  runs     one row per explore.py (or single agent.py) run
  agents   one row per competitor in a run: status, steps, cost
  steps    one row per look-and-act step: url, reason, action
  prices   one row per price an agent saw on a page, with what the plan includes

WAL mode lets several agent processes write while the dashboard reads.
"""

import json
import os
import sqlite3
import time
import uuid

REPO = os.path.join(os.path.dirname(__file__), "..")
DB = os.path.normpath(os.path.join(REPO, "output", "workshop.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
  run_id TEXT PRIMARY KEY, started REAL, source TEXT, model TEXT, goal TEXT
);
CREATE TABLE IF NOT EXISTS agents (
  run_id TEXT, site TEXT, company TEXT, status TEXT, step INTEGER DEFAULT 0,
  url TEXT, why TEXT, screenshot TEXT, page_status TEXT,
  browser_seconds REAL, units INTEGER, model_usd REAL, tokens_in INTEGER, tokens_out INTEGER,
  started REAL, updated REAL, error TEXT,
  PRIMARY KEY (run_id, site)
);
CREATE TABLE IF NOT EXISTS steps (
  run_id TEXT, site TEXT, step INTEGER, ts REAL, url TEXT, status_code INTEGER,
  page_type TEXT, description TEXT, action TEXT, link_text TEXT, why TEXT,
  screenshot TEXT, model_usd REAL
);
CREATE TABLE IF NOT EXISTS prices (
  run_id TEXT, site TEXT, company TEXT, step INTEGER, ts REAL,
  plan TEXT, amount TEXT, currency TEXT, period TEXT,
  usd_month REAL, billing TEXT, kind TEXT, url TEXT, includes TEXT
);
"""


def connect(path=DB):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    db = sqlite3.connect(path, timeout=10, isolation_level=None)  # autocommit
    db.execute("PRAGMA journal_mode=WAL")
    db.executescript(SCHEMA)
    # databases made before prices had includes (a JSON list of what the plan gives you)
    if "includes" not in [r[1] for r in db.execute("PRAGMA table_info(prices)")]:
        db.execute("ALTER TABLE prices ADD COLUMN includes TEXT")
    db.row_factory = sqlite3.Row
    return db


def new_run(db, source="live", model=None, goal=None, run_id=None):
    run_id = run_id or time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:4]
    db.execute("INSERT OR IGNORE INTO runs VALUES (?, ?, ?, ?, ?)", (run_id, time.time(), source, model, goal))
    return run_id


def agent(db, run_id, site, **fields):
    """Create or update the row for one competitor in a run."""
    fields["updated"] = time.time()
    db.execute("INSERT OR IGNORE INTO agents (run_id, site, started) VALUES (?, ?, ?)", (run_id, site, time.time()))
    cols = ", ".join(f"{k} = ?" for k in fields)
    db.execute(f"UPDATE agents SET {cols} WHERE run_id = ? AND site = ?", (*fields.values(), run_id, site))


def step(db, run_id, site, **fields):
    fields.setdefault("ts", time.time())
    cols = ", ".join(fields)
    marks = ", ".join("?" for _ in fields)
    db.execute(f"INSERT INTO steps (run_id, site, {cols}) VALUES (?, ?, {marks})", (run_id, site, *fields.values()))


def prices(db, run_id, site, company, n, url, items):
    """One row per price. includes is stored as a JSON list; a replay passes it on as it was stored."""
    now = time.time()
    db.executemany(
        "INSERT INTO prices (run_id, site, company, step, ts, plan, amount, currency, period,"
        " usd_month, billing, kind, url, includes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (run_id, site, company, n, now, p["plan"], p["amount"], p["currency"], p["period"],
             p.get("usd_month"), p.get("billing"), p.get("kind"), url,
             p["includes"] if isinstance(p.get("includes"), str) else json.dumps(p.get("includes") or []))
            for p in items
        ],
    )
