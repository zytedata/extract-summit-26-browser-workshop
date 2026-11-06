"""Lesson 05: run the lesson 04 agent on several competitors, a few at a time.

    python lessons/05-explore-competitors/explore.py                 # top 5 by mentions, 3 at a time
    python lessons/05-explore-competitors/explore.py Zyte Oxylabs ScrapingBee
    python lessons/05-explore-competitors/explore.py --top 8 --parallel 4
    python lessons/05-explore-competitors/explore.py --replay        # no network: replay a recorded run
    python lessons/05-explore-competitors/explore.py --save-sample   # keep the last run as the recording

Every competitor is its own agent.py process with its own Zyte browser. They
all write to output/workshop.db, which the dashboard reads:
    streamlit run lessons/06-report/app.py
"""

import argparse
import json
import os
import signal
import sqlite3
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared import llm, store  # noqa: E402
from shared.companies import PATH as COMPANIES, pick_url  # noqa: E402

AGENT = os.path.join(os.path.dirname(__file__), "..", "04-agent-loop", "agent.py")
OUT = os.path.join("output", "05")
SAMPLE = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample-run.db"))
FINISHED = ("done", "out of steps", "blocked", "error")

BOLD = "\033[1m"
GREY = "\033[90m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"


def top_companies(n):
    with open(COMPANIES, encoding="utf-8") as f:
        return [c["name"] for c in json.load(f)["companies"][:n]]


def site_of(name):
    from urllib.parse import urlparse
    return urlparse(pick_url(name)).netloc.removeprefix("www.")


def live(args, db):
    names = args.names or top_companies(args.top)
    sites = {name: site_of(name) for name in names}  # fails early on a typo
    model = llm.model_name(args.model)
    run_id = store.new_run(db, source="live", model=model)
    for name, site in sites.items():
        store.agent(db, run_id, site, company=name, status="waiting")

    print(f"{BOLD}Run {run_id}{RESET}: {len(names)} competitors, {args.parallel} at a time, model {model}")
    print(f"{GREY}Dashboard: streamlit run lessons/06-report/app.py{RESET}\n")

    queue = list(names)
    running = {}  # name -> (process, log file)
    t0 = time.time()
    last = {}

    def start(name):
        os.makedirs(OUT, exist_ok=True)
        log = open(os.path.join(OUT, sites[name] + ".log"), "w", encoding="utf-8")
        cmd = [sys.executable, AGENT, name, "--out", OUT, "--run-id", run_id, "--max-steps", str(args.max_steps)]
        if args.model:
            cmd += ["--model", args.model]
        running[name] = (subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT), log)

    try:
        while queue or running:
            while queue and len(running) < args.parallel:
                start(queue.pop(0))
            for name, (proc, log) in list(running.items()):
                if proc.poll() is not None:
                    log.close()
                    del running[name]
                    # The log only sits next to the journey once the agent has
                    # made its folder (it wipes it at the start).
                    src = os.path.join(OUT, sites[name] + ".log")
                    os.makedirs(os.path.join(OUT, sites[name]), exist_ok=True)  # if it died before making it
                    os.replace(src, os.path.join(OUT, sites[name], "agent.log"))
                    row = db.execute("SELECT status FROM agents WHERE run_id=? AND site=?", (run_id, sites[name])).fetchone()
                    if proc.returncode and not row["status"].startswith(FINISHED):
                        store.agent(db, run_id, sites[name], status="error", error=f"exit code {proc.returncode}")
            # Print what changed since the last look
            for row in db.execute("SELECT company, status FROM agents WHERE run_id=? ORDER BY started", (run_id,)):
                if last.get(row["company"]) != row["status"]:
                    last[row["company"]] = row["status"]
                    color = GREEN if row["status"] == "done" else YELLOW if row["status"].startswith(("error", "blocked")) else ""
                    print(f"[{time.time() - t0:5.1f}s] {row['company']:<14} {color}{row['status']}{RESET}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nstopping the agents (each one closes its browser)")
        for proc, _ in running.values():
            proc.send_signal(signal.SIGINT)
        for proc, _ in running.values():
            proc.wait(timeout=30)
        raise

    summary(db, run_id, time.time() - t0)


def summary(db, run_id, wall, recorded=False):
    rows = db.execute(
        """SELECT a.*, (SELECT COUNT(*) FROM prices p WHERE p.run_id=a.run_id AND p.site=a.site) AS prices
           FROM agents a WHERE run_id=? ORDER BY started""",
        (run_id,),
    ).fetchall()
    print(f"\n{BOLD}{'competitor':<14} {'status':<14} {'pages':<9} {'steps':>5} {'prices':>6} {'browser':>9} {'units':>5} {'model':>8}{RESET}")
    for r in rows:
        status = r["status"] if len(r["status"]) <= 14 else r["status"][:13] + "."
        print(f"{r['company']:<14} {status:<14} {r['page_status'] or '-':<9} {r['step']:>5} {r['prices']:>6} "
              f"{r['browser_seconds'] or 0:>8.0f}s {r['units'] or 0:>5} ${r['model_usd'] or 0:>7.4f}")
    browser = sum(r["browser_seconds"] or 0 for r in rows)
    units = sum(r["units"] or 0 for r in rows)
    dollars = sum(r["model_usd"] or 0 for r in rows)
    took = "took" if recorded else "in"
    print(f"\n{BOLD}{len(rows)} competitors {took} {wall:.0f}s{RESET}{' when recorded' if recorded else ''} (browsers open {browser:.0f}s in total,"
          f" running in parallel saved {max(0, browser - wall):.0f}s). {units} units, ${dollars:.4f} for the model.")

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as f:
        json.dump({"run_id": run_id, "wall_seconds": round(wall, 1), "competitors": [dict(r) for r in rows]}, f, indent=2)
        f.write("\n")
    print(f"{GREY}summary in {OUT}/summary.json, every step in {store.DB}{RESET}")


def replay(args, db):
    """Play a recorded run into the database with its original timing."""
    if not os.path.exists(args.replay):
        raise SystemExit(f"No recording at {args.replay}")
    src = sqlite3.connect(f"file:{args.replay}?mode=ro", uri=True)
    src.row_factory = sqlite3.Row
    old = src.execute("SELECT * FROM runs ORDER BY started DESC LIMIT 1").fetchone()
    run_id = store.new_run(db, source="replay", model=old["model"], goal=old["goal"])
    speed = 10 if args.fast else 1
    print(f"{BOLD}Replaying run {old['run_id']}{RESET} as {run_id}, {'10x speed' if args.fast else 'real time'}. No network used.")

    agents = src.execute("SELECT * FROM agents WHERE run_id=?", (old["run_id"],)).fetchall()
    for a in agents:  # all queued at the start, like a live run
        store.agent(db, run_id, a["site"], company=a["company"], status="waiting")
    events = []  # (when, what, row)
    for a in agents:
        events.append((a["started"], "start", a))
        events.append((a["updated"], "finish", a))
    for s in src.execute("SELECT * FROM steps WHERE run_id=?", (old["run_id"],)):
        events.append((s["ts"], "step", s))
    prices = {}
    for p in src.execute("SELECT * FROM prices WHERE run_id=?", (old["run_id"],)):
        prices.setdefault((p["site"], p["step"]), []).append(p)
    events.sort(key=lambda e: e[0])

    t0, first = time.time(), src.execute("SELECT started FROM runs WHERE run_id=?", (old["run_id"],)).fetchone()[0]
    for when, what, row in events:
        time.sleep(max(0, (when - first) / speed - (time.time() - t0)))
        site = row["site"]
        if what == "start":
            store.agent(db, run_id, site, status="connecting", step=0)
            label = "connecting"
        elif what == "step":
            label = f"step {row['step']}: {row['action']} {row['link_text'] or ''}".strip()
            company = db.execute("SELECT company FROM agents WHERE run_id=? AND site=?", (run_id, site)).fetchone()["company"]
            store.step(db, run_id, site, **{k: row[k] for k in row.keys() if k not in ("run_id", "site", "ts")})
            store.prices(db, run_id, site, company, row["step"], row["url"], [dict(p) for p in prices.get((site, row["step"]), [])])
            store.agent(db, run_id, site, status=label, step=row["step"], url=row["url"], why=row["why"], screenshot=row["screenshot"])
        else:
            keep = ("status", "page_status", "browser_seconds", "units", "model_usd", "tokens_in", "tokens_out", "error")
            store.agent(db, run_id, site, **{k: row[k] for k in keep})
            label = row["status"]
        company = db.execute("SELECT company FROM agents WHERE run_id=? AND site=?", (run_id, site)).fetchone()["company"]
        print(f"[{time.time() - t0:5.1f}s] {company:<14} {label}")

    summary(db, run_id, events[-1][0] - first, recorded=True)


def save_sample(db):
    """Keep the last finished live run as data/sample-run.db. Text only: steps,
    reasons, prices, cost. Screenshots stay out, they're pictures of other
    people's sites."""
    run = db.execute("SELECT run_id FROM runs WHERE source='live' ORDER BY started DESC LIMIT 1").fetchone()
    if not run:
        raise SystemExit("No live run in the database yet")
    if os.path.exists(SAMPLE):
        os.remove(SAMPLE)
    out = store.connect(SAMPLE)
    out.execute("PRAGMA journal_mode=DELETE")  # one plain file, nothing next to it
    for table in ("runs", "agents", "steps", "prices"):
        rows = db.execute(f"SELECT * FROM {table} WHERE run_id=?", (run["run_id"],)).fetchall()
        if rows:
            marks = ", ".join("?" for _ in rows[0].keys())
            out.executemany(f"INSERT INTO {table} ({', '.join(rows[0].keys())}) VALUES ({marks})", [tuple(r) for r in rows])
    out.close()
    print(f"Saved run {run['run_id']} to {SAMPLE}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("names", nargs="*", help="company names from data/web-scraping.json")
    parser.add_argument("--top", type=int, default=5, help="without names: the top N by mentions")
    parser.add_argument("--parallel", type=int, default=3)
    parser.add_argument("--model")
    parser.add_argument("--max-steps", type=int, default=6)
    parser.add_argument("--replay", nargs="?", const=SAMPLE, help="replay a recorded run, no network")
    parser.add_argument("--fast", action="store_true", help="with --replay: 10x speed")
    parser.add_argument("--save-sample", action="store_true", help="keep the last live run as data/sample-run.db")
    args = parser.parse_args()

    db = store.connect()
    if args.save_sample:
        save_sample(db)
    elif args.replay:
        replay(args, db)
    else:
        live(args, db)


if __name__ == "__main__":
    main()
