"""Lesson 04: the model drives one Zyte browser session until it has the prices.

    python lessons/04-agent-loop/agent.py                       # Apify
    python lessons/04-agent-loop/agent.py Oxylabs
    python lessons/04-agent-loop/agent.py Zyte --goal "find out if there is a free trial"
    python lessons/04-agent-loop/agent.py --model google/gemini-3.5-flash-lite --max-steps 4

Every step: capture the page (lesson 03), ask the model what it sees and what
to do next, do it. One browser session for the whole run, so cookies, toggles
and the IP stay the same. Output lands in output/04/<site>/.

Every step also goes into output/workshop.db, so the dashboard from lesson 06
(streamlit run lessons/06-report/app.py) shows the run while it happens.
"""

import argparse
import json
import math
import os
import shutil
import sys
import time
from urllib.parse import urlparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared import llm, store  # noqa: E402
from shared.capture import format_links, get_controls, get_links, to_markdown  # noqa: E402
from shared.companies import pick_url  # noqa: E402
from shared.zyte_cdp import open_url, settle, trace_step, zyte_page  # noqa: E402

GOAL = ("Find the pricing and capture every price set, for example both monthly and annual prices, "
        "and what each plan includes.")

MAX_MARKDOWN = 30_000
MAX_LINKS = 150

SYSTEM = """You browse a company's website to reach a goal.
Every turn you get: the goal, the steps so far, a screenshot of what is on
screen, the page text as markdown, and a numbered list of links and buttons.

Say what the page is and list the prices visible on it, with their billing
period. Then pick one action:
- click: a link or button by its number. To go somewhere, open a menu, flip a
  toggle (monthly/annual, currency), or close a cookie banner that is in the way.
- scroll: what you need is probably further down this page.
- slide: move a slider (by its number) one step to the right, to see the next
  tier of a plan. The list shows where each slider is ("at 0 of 2").
- done: the goal is reached, or it can't be reached from here.

Take the most direct path. Don't repeat a click unless the page changed.
Prices you reported in earlier steps are saved, the steps so far list them.
If prices change with a toggle, put the toggle state in the period of every
price ("month, billed monthly" / "month, billed annually"), then flip it once
so the other set gets captured. Don't flip back to double check, what you
reported is saved. When every price set is in the steps so far or on this
page, say done.

For every price also fill in the comparable form: usd_month is what the plan
costs per month in USD as a number (for annual billing, the per-month price),
null when it's usage based, custom or not in USD. billing is monthly, annual
or none. kind is subscription, usage, custom or free.
includes is what the plan gives you, in the company's own units, as the page
says it: "$19 prepaid usage", "2,000 credits", "100K requests", "10 tasks".
The 2 to 4 things that set the plan apart, short. Empty if the page doesn't say.
If the page is a block page (CAPTCHA, access denied), say done.
Answer with JSON only, in the shape you were given. Use only what is on the page."""

SCHEMA = {
    "type": "object",
    "properties": {
        "page_type": {
            "type": "string",
            "enum": ["home", "pricing", "product", "about", "blog", "docs", "login", "block_page", "other"],
        },
        "description": {"type": "string", "description": "one sentence: what is on screen now"},
        "prices": {
            "type": "array",
            "description": "prices visible right now, empty if none",
            "items": {
                "type": "object",
                "properties": {
                    "plan": {"type": "string"},
                    "amount": {"type": "string", "description": "as shown, e.g. '49', 'from 0.13', 'custom'"},
                    "currency": {"type": "string"},
                    "period": {"type": "string", "description": "with the toggle state if there is one, e.g. 'month, billed monthly', 'month, billed annually', 'per 1k requests'"},
                    "usd_month": {"type": ["number", "null"], "description": "per month in USD, null if usage based or custom"},
                    "billing": {"type": "string", "enum": ["monthly", "annual", "none"]},
                    "kind": {"type": "string", "enum": ["subscription", "usage", "custom", "free"]},
                    "includes": {
                        "type": "array", "items": {"type": "string"},
                        "description": "what the plan gives you in the company's own units, short, e.g. '$19 prepaid usage', '2,000 credits'",
                    },
                },
                "required": ["plan", "amount", "currency", "period", "usd_month", "billing", "kind", "includes"],
                "additionalProperties": False,
            },
        },
        # Reason first, then the action: the model writes fields in order.
        "why": {"type": "string", "description": "one sentence: what to do next and why"},
        "action": {"type": "string", "enum": ["click", "scroll", "slide", "done"]},
        "link": {"type": ["integer", "null"], "description": "number of the link or button to click, null otherwise"},
    },
    "required": ["page_type", "description", "prices", "why", "action", "link"],
    "additionalProperties": False,
}

BOLD = "\033[1m"
GREY = "\033[90m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RESET = "\033[0m"
OPEN = f"{GREEN}[browser OPEN]{RESET}"
CLOSED = f"{GREY}[browser closed]{RESET}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", default="Apify", help="company name from data/web-scraping.json, or a URL")
    parser.add_argument("--goal", default=GOAL)
    parser.add_argument("--model", help=f"OpenRouter model id, default: {llm.model_name()}")
    parser.add_argument("--max-steps", type=int, default=6)
    parser.add_argument("--hint", help="notes from a review of an earlier attempt (lesson 05 --judge)")
    parser.add_argument("--out", default=os.path.join("output", "04"), help="folder for the journey, one subfolder per site")
    parser.add_argument("--run-id", default=os.environ.get("WORKSHOP_RUN_ID"), help="add to this run in the database (explore.py sets it)")
    args = parser.parse_args()

    url = pick_url(args.target)
    site = urlparse(url).netloc.removeprefix("www.")
    company = site if args.target.startswith("http") else args.target
    out = os.path.join(args.out, site)
    shutil.rmtree(out, ignore_errors=True)  # a fresh journey every run
    os.makedirs(out)
    model = llm.model_name(args.model)
    t0 = time.time()

    # The dashboard reads this. One row per step, one per price, plus a status
    # row for this competitor that we update as we go.
    db = store.connect()
    run_id = store.new_run(db, model=model, goal=args.goal, run_id=args.run_id)
    # started = now, not when explore.py queued it: the dashboard and the
    # replay show the wait in the queue.
    store.agent(db, run_id, site, company=company, status="connecting", step=0, started=time.time())
    try:
        run(args, url, site, company, out, model, t0, db, run_id)
    except BaseException as e:  # also Ctrl+C and SystemExit, so the dashboard doesn't wait forever
        store.agent(db, run_id, site, status="error", error=f"{type(e).__name__}: {e}"[:300])
        raise


def run(args, url, site, company, out, model, t0, db, run_id):

    def now():
        return time.time() - t0

    def step(state, text):
        print(f"\n{BOLD}[{now():5.1f}s]{RESET} {state} {BOLD}{text}{RESET}")

    def info(text):
        print(f"        {text}")

    print(f"{BOLD}Goal:{RESET} {args.goal}")
    print(f"{BOLD}Model:{RESET} {model}, max {args.max_steps} steps")

    journey, history, model_calls = [], [], []
    page_loads = 0
    in_page_clicks = 0  # clicks that changed the page without a new URL
    codes = []  # HTTP status of every page the browser navigated to
    final = f"out of steps ({args.max_steps})"

    def count_load(_):
        nonlocal page_loads
        page_loads += 1

    def watch(p):
        p.on("load", count_load)
        p.on("response", lambda r: codes.append(r.status) if r.request.is_navigation_request() and r.frame == p.main_frame else None)

    step(CLOSED, "Connect to browser.zyte.com")
    trace = os.path.join(out, "trace.zip")
    with zyte_page(ttl=180, trace=trace) as page:
        opened = now()
        info(f"connected in {opened:.1f}s, billing started")
        info(f"recording a Playwright trace to {trace}")
        tracing = page.context.tracing  # one per session, also covers new tabs
        watch(page)
        store.agent(db, run_id, site, status="opening the homepage")

        step(OPEN, f"Go to {url}")
        with trace_step(page, f"Open {url}"):
            open_url(page, url)

        for n in range(1, args.max_steps + 1):
            # In the trace viewer every step is two groups: "look" (capture,
            # then the browser waits for the model) and the action, titled
            # with what the model decided and why.
            tracing.group(f"Step {n}: look at the page, ask the model")
            step(OPEN, f"Step {n}: capture {page.url}")
            shot = page.screenshot(type="jpeg", quality=70)
            md = to_markdown(page.content())
            links = get_links(page)
            controls = get_controls(page)  # for the review in lesson 05: sliders, dropdowns, open dialogs
            info(f"screenshot {len(shot) // 1024} KB, markdown {len(md) // 1024} KB, {len(links)} links and buttons")
            latest = os.path.join(out, "latest.jpg")  # what the dashboard shows right now
            with open(latest, "wb") as f:
                f.write(shot)
            store.agent(db, run_id, site, status=f"step {n}: model is looking", step=n, url=page.url, screenshot=latest)

            so_far = "\n".join(history) or "none, this is the first page"
            parts = [
                llm.text_part(f"Goal: {args.goal}\n\n"
                              + (f"A review of an earlier attempt said: {args.hint}\n\n" if args.hint else "")
                              + f"Steps so far:\n{so_far}"),
                llm.image_part(shot),
                llm.text_part(f"URL: {page.url}\n\n# Page text (markdown)\n\n{md[:MAX_MARKDOWN]}"),
                llm.text_part(f"# Links and buttons\n\n{format_links(links[:MAX_LINKS])}"),
            ]
            step(OPEN, f"Step {n}: ask {model}  {GREY}(browser waits, same page, same cookies){RESET}")
            start = now()
            answer, stats = llm.ask(SYSTEM, parts, SCHEMA, model=args.model)
            model_calls.append((start, now(), stats))
            cost = f"${stats['cost_usd']:.4f}" if stats["cost_usd"] is not None else "cost n/a"
            info(f"{stats['seconds']}s, {stats['input_tokens']} tokens in, {stats['output_tokens']} out, {cost}")
            for line in json.dumps(answer, indent=2, ensure_ascii=False).splitlines():
                info(f"{CYAN}{line}{RESET}")
            tracing.group_end()
            store.prices(db, run_id, site, company, n, page.url, answer["prices"])

            name = f"{n:02d}_{answer['page_type']}"
            with open(os.path.join(out, name + ".jpg"), "wb") as f:
                f.write(shot)
            with open(os.path.join(out, name + ".md"), "w", encoding="utf-8") as f:
                f.write(md)

            target = None
            if answer["action"] in ("click", "slide"):
                k = answer["link"]
                target = links[k - 1] if k and 1 <= k <= len(links) else None
            record = {
                "step": n,
                "url": page.url,
                "page_type": answer["page_type"],
                "description": answer["description"],
                "prices": answer["prices"],
                "action": answer["action"],
                "link": answer["link"],
                "link_text": target["text"] if target else None,
                "why": answer["why"],
                "screenshot": name + ".jpg",
                "controls": controls,
                "model": stats,
            }

            # What the model will see as "steps so far" next time. With the
            # prices in it, it knows when it has everything.
            saved = "; ".join(f"{p['plan']} {p['amount']} {p['currency']}/{p['period']}" for p in answer["prices"])
            saved = f" Prices saved: {saved}." if saved else ""

            label = f"{answer['action']} {answer['link']} {target['text']!r}" if target else answer["action"]
            store.step(db, run_id, site, step=n, url=page.url, status_code=codes[-1] if codes else None,
                       page_type=answer["page_type"], description=answer["description"], action=answer["action"],
                       link_text=target["text"] if target else None, why=answer["why"],
                       screenshot=os.path.join(out, name + ".jpg"), model_usd=stats["cost_usd"])
            store.agent(db, run_id, site, status=f"step {n}: {label}", why=answer["why"],
                        screenshot=os.path.join(out, name + ".jpg"))

            if answer["page_type"] == "block_page":
                # Zyte's browser handles unblocking. If we still see one, say so, don't work around it.
                step(OPEN, f"{YELLOW}Step {n}: the model says this is a block page. Stopping, worth reporting.{RESET}")
                final = "blocked (unexpected, worth reporting)"
                journey.append(record)
                break

            if answer["action"] == "done":
                final = "done"
                tracing.group(f"Step {n}: done. Model: {answer['why']}")
                tracing.group_end()
                journey.append(record)
                history.append(f"{n}. {page.url} ({answer['page_type']}): done.{saved}")
                break

            before = page.url
            tracing.group(f"Step {n}: {label}. Model: {answer['why']}")
            if answer["action"] == "slide" and target is not None:
                # A slider isn't clicked, it's moved: focus it and press the right arrow once.
                step(OPEN, f"Step {n}: move slider {answer['link']} one step")
                try:
                    el = page.locator(f'[data-agent-n="{answer["link"]}"]').first
                    el.focus(timeout=5_000)
                    el.press("ArrowRight")
                    page.wait_for_timeout(1500)  # the price animates to the new tier
                    did = f"moved slider {answer['link']} one step"
                    in_page_clicks += 1
                except Exception as e:
                    info(f"{YELLOW}could not move it: {str(e).splitlines()[0]}{RESET}")
                    did = f"tried to move slider {answer['link']}, failed"
            elif answer["action"] == "scroll":
                step(OPEN, f"Step {n}: scroll down")
                page.mouse.wheel(0, 900)
                page.wait_for_timeout(800)
                did = "scrolled down"
            elif target is None:
                step(OPEN, f"Step {n}: {YELLOW}link {answer['link']} is not in the list, nothing clicked{RESET}")
                did = f"tried to click {answer['link']}, no such link"
            else:
                step(OPEN, f"Step {n}: click {answer['link']} {target['text']!r}")
                tabs = len(page.context.pages)
                try:
                    page.locator(f'[data-agent-n="{answer["link"]}"]').first.click(timeout=5_000)
                    page.wait_for_timeout(1000)  # give a navigation or a toggle time to start
                    if len(page.context.pages) > tabs:  # opened a new tab: follow it
                        page = page.context.pages[-1]
                        watch(page)
                        info("it opened a new tab, carrying on there")
                    settle(page)  # a click that loads a page: wait for it, but not forever
                    did = f"clicked {answer['link']} {target['text']!r}"
                except Exception as e:
                    # Usually a link inside a closed dropdown menu: it's in the
                    # page, but not clickable until the menu opens on hover.
                    info(f"{YELLOW}click failed: {str(e).splitlines()[0]}{RESET}")
                    if target["href"].startswith("http"):
                        info(f"it's a link, so open its URL instead: {target['href']}")
                        open_url(page, target["href"])
                        did = f"click on {answer['link']} {target['text']!r} failed, opened its URL instead"
                    else:
                        did = f"click on {answer['link']} {target['text']!r} failed"
                if page.url != before:
                    info(f"now on {page.url}")
                elif did.startswith("clicked"):
                    in_page_clicks += 1
                    info(f"same URL, the page changed in place {GREY}(a new browser would lose this){RESET}")

            tracing.group_end()
            record["did"] = did
            journey.append(record)
            history.append(f"{n}. {before} ({answer['page_type']}): {did}.{saved}")
        else:
            step(OPEN, f"{YELLOW}Stopped after {args.max_steps} steps{RESET}")

        step(OPEN, "Close the session (Browser.close over CDP)")
    closed = now()

    with open(os.path.join(out, "journey.jsonl"), "w", encoding="utf-8") as f:
        for record in journey:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # What did we find?
    print(f"\n{BOLD}Prices found{RESET}")
    seen = set()
    for r in journey:
        for p in r["prices"]:
            key = (p["plan"], p["amount"], p["currency"], p["period"])
            if key not in seen:
                seen.add(key)
                print(f"  step {r['step']}  {p['plan']:<22} {p['amount']:>10} {p['currency']:<4} / {p['period']}")
                if p.get("includes"):
                    print(f"  {GREY}{'':<30} includes: {', '.join(p['includes'])}{RESET}")
    if not seen:
        print("  none")

    # What did it cost?
    session = closed - opened
    blocks = math.ceil(session / 15)
    units = max(page_loads, blocks)
    steps = len(journey)
    tokens_in = sum(s["input_tokens"] or 0 for _, _, s in model_calls)
    tokens_out = sum(s["output_tokens"] or 0 for _, _, s in model_calls)
    dollars = sum(s["cost_usd"] or 0 for _, _, s in model_calls)
    thinking = sum(b - a for a, b, _ in model_calls)

    print(f"\n{BOLD}Cost{RESET}")
    which = "time" if blocks > page_loads else "page loads"
    print(f"  browser: 1 session, open {session:.0f}s = {blocks} x 15s blocks, {page_loads} full page load(s)"
          f" -> {units} units ({which} set the bill)")
    print(f"  model:   {steps} calls, {tokens_in} tokens in, {tokens_out} out, ${dollars:.4f}")
    print(f"  {thinking:.0f}s of the {session:.0f}s the browser was open, the model was thinking")
    print(f"  a new browser per step: {steps} sessions -> at least {steps} units, {steps} x ~3s to connect"
          + (f", and {in_page_clicks} in-page change(s) lost (toggle, menu, banner)" if in_page_clicks else ""))

    store.agent(db, run_id, site, status=final, browser_seconds=round(session, 1), units=units,
                model_usd=round(dollars, 5), tokens_in=tokens_in, tokens_out=tokens_out,
                page_status=", ".join(str(c) for c in sorted(set(codes))))

    # Timeline: one row for the browser, one for the model calls.
    width = 60
    end = now()

    def bar(spans, char):
        row = [" "] * width
        for a, b in spans:
            for i in range(int(a / end * width), max(int(a / end * width) + 1, int(b / end * width))):
                row[min(i, width - 1)] = char
        return "".join(row)

    print(f"\n{BOLD}Timeline{RESET} {GREY}(0s -> {end:.0f}s){RESET}")
    print(f"  browser open  {GREEN}{bar([(opened, closed)], '#')}{RESET}")
    print(f"  model         {CYAN}{bar([(a, b) for a, b, _ in model_calls], '#')}{RESET}")

    print(f"\n{BOLD}Done in {end:.1f}s.{RESET} Journey in {out}/:")
    for r in journey:
        print(f"  {r['screenshot']:<16} {r['action']:<6} {r.get('link_text') or ''}")
    print("  journey.jsonl")
    print(f"\nReplay the whole session, step by step: {BOLD}playwright show-trace {trace}{RESET}")
    print(f"{GREY}(or drop the file on https://trace.playwright.dev, it stays in your browser){RESET}")


if __name__ == "__main__":
    main()
