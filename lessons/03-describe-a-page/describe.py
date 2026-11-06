"""Lesson 03: open a competitor's page in a Zyte browser and ask a model what it is.

    python lessons/03-describe-a-page/describe.py                  # Apify, top of the list
    python lessons/03-describe-a-page/describe.py Oxylabs          # any name from data/web-scraping.json
    python lessons/03-describe-a-page/describe.py https://www.zyte.com/pricing/
    python lessons/03-describe-a-page/describe.py Zyte --model google/gemini-3.5-flash-lite

The browser part is the same as lesson 01: screenshot, markdown, numbered
links. New here: all three go to a model through OpenRouter, and the model
answers in a fixed JSON shape. Output lands in output/03/<site>/.
"""

import argparse
import json
import math
import os
import sys
import time
from urllib.parse import urlparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared import llm  # noqa: E402
from shared.capture import format_links, get_links, to_markdown  # noqa: E402
from shared.zyte_cdp import zyte_page  # noqa: E402

COMPANIES = os.path.join(os.path.dirname(__file__), "..", "..", "data", "web-scraping.json")

# Keep what we send small. Long pages get cut, and we say so.
MAX_MARKDOWN = 30_000  # characters, about 7-8k tokens
MAX_LINKS = 150

SYSTEM = """You look at one web page of a company and say what it is.
You get a screenshot of the top of the page, the page text as markdown, and a
numbered list of the links and buttons on it.
Answer with JSON only, in the shape you were given. Use only what is on the
page. If there are no prices, return an empty list, don't guess."""

SCHEMA = {
    "type": "object",
    "properties": {
        "company": {"type": "string", "description": "company name as the page shows it"},
        "description": {"type": "string", "description": "two sentences: what this page is and what the company sells"},
        "page_type": {
            "type": "string",
            "enum": ["home", "pricing", "product", "about", "blog", "docs", "login", "block_page", "other"],
        },
        "prices": {
            "type": "array",
            "description": "prices visible on this page",
            "items": {
                "type": "object",
                "properties": {
                    "plan": {"type": "string"},
                    "amount": {"type": "string", "description": "as shown, e.g. '49', 'from 0.13', 'custom'"},
                    "currency": {"type": "string"},
                    "period": {"type": "string", "description": "month, year, per 1k requests, one-off, ..."},
                },
                "required": ["plan", "amount", "currency", "period"],
                "additionalProperties": False,
            },
        },
        # "why" comes before the number on purpose: the model writes fields in
        # order, so it reasons first and then picks. The other way round it can
        # pick a number and then explain a different one.
        "why": {"type": "string", "description": "one sentence: which link leads to pricing and why"},
        "pricing_link": {
            "type": ["integer", "null"],
            "description": "number of that link in the list, null if none",
        },
    },
    "required": ["company", "description", "page_type", "prices", "why", "pricing_link"],
    "additionalProperties": False,
}

BOLD = "\033[1m"
GREY = "\033[90m"
GREEN = "\033[32m"
CYAN = "\033[36m"
RESET = "\033[0m"

OPEN = f"{GREEN}[browser OPEN]{RESET}"
CLOSED = f"{GREY}[browser closed]{RESET}"


def pick_url(target):
    if target.startswith("http"):
        return target
    with open(COMPANIES, encoding="utf-8") as f:
        companies = json.load(f)["companies"]
    for c in companies:
        if c["name"].lower() == target.lower():
            return c["homepage"]
    names = ", ".join(c["name"] for c in companies)
    raise SystemExit(f"{target!r} is not in data/web-scraping.json. Pick one of: {names}. Or pass a URL.")


def preview(parts):
    """The message we send, with the base64 image replaced by its size."""
    shown = []
    for p in parts:
        if p["type"] == "image_url":
            shown.append({"type": "image_url", "image_url": f"<jpeg, {len(p['image_url']['url']) // 1024} KB of base64>"})
        else:
            text = p["text"]
            shown.append({"type": "text", "text": text[:200] + (f"... <{len(text) // 1024} KB more>" if len(text) > 200 else "")})
    return shown


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", default="Apify", help="company name from data/web-scraping.json, or a URL")
    parser.add_argument("--model", help=f"OpenRouter model id, default: {llm.model_name()}")
    args = parser.parse_args()

    url = pick_url(args.target)
    site = urlparse(url).netloc.removeprefix("www.")
    out = os.path.join("output", "03", site)
    os.makedirs(out, exist_ok=True)
    model = llm.model_name(args.model)
    t0 = time.time()

    def now():
        return time.time() - t0

    def step(state, text):
        print(f"\n{BOLD}[{now():5.1f}s]{RESET} {state} {BOLD}{text}{RESET}")

    def info(text):
        print(f"        {text}")

    # Browser part. Everything inside the "with" runs while a Chrome is
    # running for you at Zyte, and that's what you pay for.
    step(CLOSED, "Connect to browser.zyte.com")
    with zyte_page(ttl=90) as page:
        opened = now()
        info(f"connected in {opened:.1f}s. A Chrome is running for you at Zyte now, billing started.")

        # Waiting for "load" is enough. We tried an extra wait for a quiet
        # network: busy sites never go quiet, it cost 5s per page and the
        # links and screenshot came out the same.
        step(OPEN, f"Go to {url} (wait for the load event)")
        response = page.goto(url, wait_until="load")
        info(f"status {response.status if response else '?'}, title: {page.title()!r}")
        if page.url != url:
            info(f"redirected to {page.url}")

        step(OPEN, "Screenshot (top of the page, what the model will look at)")
        shot = page.screenshot(type="jpeg", quality=70)
        info(f"{len(shot) // 1024} KB jpeg")

        step(OPEN, "HTML -> markdown (what the model will read)")
        html = page.content()
        md = to_markdown(html)
        info(f"HTML {len(html) // 1024} KB -> markdown {len(md) // 1024} KB")

        step(OPEN, "List links and buttons, numbered")
        links = get_links(page)
        final_url = page.url
        info(f"{len(links)} links and buttons")

        step(OPEN, "Close the session (Browser.close over CDP)")
        closing = now()
    closed = now()
    session = closed - opened
    blocks = math.ceil(session / 15)
    info(f"closed in {closed - closing:.1f}s. The browser was open for {session:.1f}s.")
    info(f"1 page load, {session:.0f}s = {blocks} x 15s block(s) -> billed as {max(1, blocks)} unit(s), whichever is higher")
    info("From here on no browser is running. The model only sees what we captured.")

    cut = len(md) > MAX_MARKDOWN
    md_sent = md[:MAX_MARKDOWN]
    links_text = format_links(links[:MAX_LINKS])
    with open(os.path.join(out, "screenshot.jpg"), "wb") as f:
        f.write(shot)
    with open(os.path.join(out, "page.md"), "w", encoding="utf-8") as f:
        f.write(md)
    with open(os.path.join(out, "links.txt"), "w", encoding="utf-8") as f:
        f.write(links_text + "\n")

    step(CLOSED, f"Build the message for {model}")
    parts = [
        llm.image_part(shot),
        llm.text_part(f"URL: {final_url}\n\n# Page text (markdown)\n\n{md_sent}"),
        llm.text_part(f"# Links and buttons\n\n{links_text}"),
    ]
    if cut:
        info(f"markdown is {len(md) // 1000}k characters, sending the first {MAX_MARKDOWN // 1000}k")
    if len(links) > MAX_LINKS:
        info(f"{len(links)} links, sending the first {MAX_LINKS}")
    request = {"model": model, "system": SYSTEM, "user": preview(parts), "answer_schema": list(SCHEMA["properties"])}
    with open(os.path.join(out, "request.json"), "w", encoding="utf-8") as f:
        json.dump(request, f, indent=2, ensure_ascii=False)
        f.write("\n")
    for line in json.dumps(request, indent=2, ensure_ascii=False).splitlines():
        info(f"{GREY}{line}{RESET}")

    step(CLOSED, f"Send it to OpenRouter -> {model}")
    model_start = now()
    answer, stats = llm.ask(SYSTEM, parts, SCHEMA, model=args.model)
    model_end = now()
    cost = f"${stats['cost_usd']:.4f}" if stats["cost_usd"] is not None else "cost n/a"
    info(f"{stats['seconds']}s, {stats['input_tokens']} tokens in, {stats['output_tokens']} out, {cost}")

    with open(os.path.join(out, "answer.json"), "w", encoding="utf-8") as f:
        json.dump({"url": final_url, "answer": answer, "stats": stats}, f, indent=2, ensure_ascii=False)
        f.write("\n")

    step(CLOSED, "The answer, as JSON (exactly what the model sent back)")
    for line in json.dumps(answer, indent=2, ensure_ascii=False).splitlines():
        info(f"{CYAN}{line}{RESET}")

    step(CLOSED, "What our code does with it")
    info(f"{BOLD}{answer['company']}{RESET}, page type: {answer['page_type']}, {len(answer['prices'])} price(s)")
    n = answer["pricing_link"]
    if n and 1 <= n <= len(links):
        link = links[n - 1]
        info(f"pricing_link {n} -> {link['text']!r} {link['href']}")
        info(f"{GREY}that's the click lesson 04 will make{RESET}")
    else:
        info("no pricing link")

    end = now()
    phases = [
        ("connect", 0, opened, GREY),
        ("browser open", opened, closed, GREEN),
        ("model", model_start, model_end, CYAN),
    ]
    print(f"\n{BOLD}Timeline{RESET} {GREY}(each mark = {end / 50:.1f}s){RESET}")
    for name, a, b, color in phases:
        bar = " " * round(a / end * 50) + "#" * max(1, round((b - a) / end * 50))
        print(f"  {name:<13} {color}{bar:<50}{RESET} {a:5.1f}s -> {b:5.1f}s  ({b - a:.1f}s)")
    print(f"\n{BOLD}Done in {now():.1f}s.{RESET} Browser {session:.1f}s, model {stats['seconds']}s. Look at:")
    for name in ["screenshot.jpg", "page.md", "links.txt", "request.json", "answer.json"]:
        print(f"  {out}/{name}")


if __name__ == "__main__":
    main()
