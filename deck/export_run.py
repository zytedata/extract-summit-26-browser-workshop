"""Turn the recorded run (data/sample-run.db) into deck/run.js for replay.html.

    python deck/export_run.py                      # data/sample-run.db -> deck/run.js
    python deck/export_run.py output/workshop.db   # or the newest run in any workshop database

Re-record first with lesson 05 if you want a fresh one:
    python lessons/05-explore-competitors/explore.py && python lessons/05-explore-competitors/explore.py --save-sample

Times are seconds from the start of the run, so the page can play it back with
the real timing. Text only, like the recording: no screenshots of other people's sites.
"""

import json
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "data", "sample-run.db")
OUT = os.path.join(HERE, "run.js")

db = sqlite3.connect(f"file:{SRC}?mode=ro", uri=True)
db.row_factory = sqlite3.Row
run = db.execute("SELECT * FROM runs WHERE source='live' ORDER BY started DESC LIMIT 1").fetchone()
t0 = run["started"]
rel = lambda t: round(t - t0, 2) if t else None  # noqa: E731

agents = [
    {"site": a["site"], "company": a["company"], "start": rel(a["started"]), "end": rel(a["updated"]),
     "status": a["status"], "steps": a["step"], "browser_seconds": a["browser_seconds"], "units": a["units"],
     "model_usd": a["model_usd"], "page_status": a["page_status"]}
    for a in db.execute("SELECT * FROM agents WHERE run_id=? ORDER BY started", (run["run_id"],))
]
steps = [
    {"site": s["site"], "step": s["step"], "t": rel(s["ts"]), "url": s["url"], "page_type": s["page_type"],
     "action": s["action"], "link_text": s["link_text"], "why": s["why"], "model_usd": s["model_usd"]}
    for s in db.execute("SELECT * FROM steps WHERE run_id=? ORDER BY ts", (run["run_id"],))
]
prices = [
    {"site": p["site"], "company": p["company"], "step": p["step"], "plan": p["plan"], "amount": p["amount"],
     "currency": p["currency"], "period": p["period"], "usd_month": p["usd_month"], "billing": p["billing"],
     "kind": p["kind"], "includes": json.loads(p["includes"] or "[]")}
    for p in db.execute("SELECT * FROM prices WHERE run_id=? ORDER BY ts", (run["run_id"],))
]
data = {"run_id": run["run_id"], "model": run["model"], "goal": run["goal"],
        "recorded": run["run_id"][:8], "agents": agents, "steps": steps, "prices": prices}
with open(OUT, "w", encoding="utf-8") as f:
    f.write("// Made by deck/export_run.py from a recorded lesson 05 run. Don't edit by hand.\n")
    f.write("const RUN = " + json.dumps(data, indent=1, ensure_ascii=False) + ";\n")
print(f"run {run['run_id']}: {len(agents)} competitors, {len(steps)} steps, {len(prices)} prices -> {os.path.relpath(OUT)}")
