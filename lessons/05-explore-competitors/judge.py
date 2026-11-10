"""Bonus for lesson 05: review what an agent found, and tell it what it missed.

    python lessons/05-explore-competitors/judge.py output/05/brightdata.com   # review one finished journey
    python lessons/05-explore-competitors/explore.py --judge                  # review every agent, retry once with the hint

Two layers:

1. Checks: plain code, free. Things we know go wrong: a price with no number
   in it ("$/1K requests"), a slider left at its first stop (more tiers behind
   it), a popup still open over the page, no prices at all.
2. Judge: a model looks at the last page the agent saw (screenshot + text)
   next to the plans the agent saved, and says what's missing or wrong. It
   writes a hint for a second attempt: which control to use, what to read.

explore.py --judge runs the agent again with that hint when the judge says the
result isn't complete. That's how the agent learns from its own run: the
review of attempt 1 goes into the prompt of attempt 2.
"""

import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared import llm  # noqa: E402

SYSTEM = """You review the result of a pricing research agent. It browsed a company's
website and saved the plans it found. You get the steps it took, the plans it
saved, the results of some automatic checks, and the last page it looked at
(screenshot and page text).

Only one question matters: is a plan, a price set or a price missing?
- missing: a plan on the page that wasn't saved; a price set that wasn't saved
  (monthly or annual, a tier of a slider or dropdown); a saved price with no
  amount where the page shows one; a saved amount that contradicts the page.
  Be concrete: "Scale has 3 tiers on the slider, only 2 were saved".
- Prices saved on earlier steps in another state (the other side of a
  monthly/annual toggle, another slider position) can't be seen on this page.
  Trust them unless the page contradicts them.
- Not missing: duplicates, wording or number formats, "includes" lists that
  are shorter than the page's feature list, prices behind "contact sales".
  Put those in notes if you want, they don't block.
hint: one or two sentences for the agent's next attempt: what to do on the page
and what to read. Empty if nothing is missing.
Answer with JSON only, in the shape you were given."""

SCHEMA = {
    "type": "object",
    "properties": {
        "missing": {"type": "array", "items": {"type": "string"}},
        "notes": {"type": "array", "items": {"type": "string"}},
        "hint": {"type": "string"},
    },
    "required": ["missing", "notes", "hint"],
    "additionalProperties": False,
}


def load(site_dir):
    """The journey an agent left in output/05/<site>/: one record per step."""
    with open(os.path.join(site_dir, "journey.jsonl"), encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def saved_plans(journey):
    """Every price the agent saved, once."""
    seen, out = set(), []
    for r in journey:
        for p in r["prices"]:
            key = (p["plan"], p["amount"], p["period"])
            if key not in seen:
                seen.add(key)
                out.append(p)
    return out


def checks(journey):
    """Free checks in plain code: (gaps, hints). Each one is a short sentence.

    gaps block: something is certainly missing. hints don't: they're things
    worth a look (a popup still open, a dropdown), the judge decides.
    """
    problems, info = [], []
    plans = saved_plans(journey)
    if not plans:
        problems.append("No prices were saved.")
    for p in plans:
        if p.get("kind") not in ("free", "custom") and not re.search(r"\d", p["amount"]):
            problems.append(f"{p['plan']}: the amount {p['amount']!r} has no number in it.")
    last = journey[-1] if journey else {}
    controls = last.get("controls") or {}
    for s in controls.get("sliders", []):
        if s.get("max") and s.get("at", 0) < s["max"]:
            problems.append(f"A slider on the last page is at {s['at']} of {s['max']}: there are tiers the agent didn't see.")
    if last and last.get("action") != "done":
        problems.append("The agent ran out of steps before it said done.")
    if controls.get("dialogs"):
        info.append("A dialog (cookie popup?) was still open over the last page.")
    if controls.get("selects"):
        info.append(f"The last page has {controls['selects']} dropdown(s): they may change the prices.")
    return problems, info


def review(site_dir, model=None):
    """Checks + the judge's verdict for one finished journey."""
    journey = load(site_dir)
    found, info = checks(journey)
    last = journey[-1]
    shot = os.path.join(site_dir, last["screenshot"])
    md_files = sorted(glob.glob(os.path.join(site_dir, "*.md")))
    page = open(md_files[-1], encoding="utf-8").read() if md_files else ""
    plans = [{k: p.get(k) for k in ("plan", "amount", "period", "includes")} for p in saved_plans(journey)]
    steps = "\n".join(f"{r['step']}. {r['url']}: {r.get('did') or r['action']}" for r in journey)
    parts = [
        llm.text_part(f"# Steps the agent took\n\n{steps}\n\nURL of the last page: {last['url']}\n\n"
                      f"# Plans the agent saved\n\n{json.dumps(plans, indent=1, ensure_ascii=False)}\n\n"
                      f"# Automatic checks\n\n" + ("\n".join(f"- {c}" for c in found + info) or "- nothing found")),
    ]
    if os.path.exists(shot):
        with open(shot, "rb") as f:
            parts.append(llm.image_part(f.read()))
    parts.append(llm.text_part(f"# Last page text (markdown)\n\n{page[:20000]}"))
    verdict, stats = llm.ask(SYSTEM, parts, SCHEMA, model=model)
    # Complete = the judge found nothing missing and the checks found nothing. The
    # checks are facts: a slider left halfway is a gap, whatever the model says.
    complete = not verdict["missing"] and not found
    hint = verdict["hint"] or ("" if complete else " ".join(found))
    return {"checks": found + info, "complete": complete, "issues": verdict["missing"], "notes": verdict["notes"],
            "hint": hint, "cost_usd": stats["cost_usd"], "seconds": stats["seconds"]}


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    r = review(sys.argv[1])
    print("Steps:")
    for step in load(sys.argv[1]):
        print(f"  {step['step']}. {step['url'].replace('https://', '')}: {step.get('did') or step['action']}")
    print("\nChecks:")
    for c in r["checks"] or ["nothing found"]:
        print(f"  - {c}")
    print(f"\nJudge: {'complete' if r['complete'] else 'NOT complete'}  ({r['seconds']}s, ${r['cost_usd'] or 0:.4f})")
    for i in r["issues"]:
        print(f"  - missing: {i}")
    for i in r["notes"]:
        print(f"  - note: {i}")
    if r["hint"]:
        print(f"\nHint for the next attempt: {r['hint']}")


if __name__ == "__main__":
    main()
