"""Lesson 01: one Zyte browser session, step by step, with the CDP trace.

    python lessons/01-first-session/first_session.py
    python lessons/01-first-session/first_session.py https://some-site.example
    python lessons/01-first-session/first_session.py --proxy-type residential --region IE

Every step prints what it does, how long it took, and the CDP messages it
caused. Output lands in output/01/.
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared import cdp_trace  # noqa: E402

OUT = os.path.join("output", "01")
trace = cdp_trace.start(os.path.join(OUT, "cdp_trace.log"))  # before connecting

from shared.capture import format_links, get_links, to_markdown  # noqa: E402
from shared.zyte_cdp import zyte_page  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("url", nargs="?", default="https://quotes.toscrape.com/js/")
parser.add_argument("--proxy-type", choices=["datacenter", "residential"], help="default: Zyte picks for the site")
parser.add_argument("--region", help="country code like IE, US, DE. Default: Zyte picks for the site")
args = parser.parse_args()
URL = args.url

BOLD = "\033[1m"
RESET = "\033[0m"
t0 = time.time()
step_no = 0


def step(text):
    global step_no
    step_no += 1
    print(f"\n{BOLD}[{time.time() - t0:5.1f}s] {step_no}. {text}{RESET}")


def info(text):
    print(f"      {text}")


def kb(n):
    return f"{n / 1024:.1f} KB"


proxy = f"proxy_type={args.proxy_type or 'auto'}, proxy_region={args.region or 'auto'}"
step(f"Connect to browser.zyte.com over CDP (API key in the auth header, ttl=120, {proxy})")
with zyte_page(ttl=120, proxy_type=args.proxy_type, proxy_region=args.region) as page:
    info("connected. A Chrome is now running for you on Zyte's side. Billing started.")
    trace.show()

    step(f"Go to {URL} (first page of the session: Zyte picks the proxy for this site now)")
    response = page.goto(URL, wait_until="load")
    info(f"status {response.status}, title: {page.title()!r}")
    trace.show()

    step("Wait for the page to settle (JavaScript, late requests)")
    try:
        page.wait_for_load_state("networkidle", timeout=5000)
        info("network idle")
    except Exception:
        info("still busy after 5s, carrying on")
    trace.show()

    step("Screenshot (what the model will look at)")
    shot = page.screenshot(path=os.path.join(OUT, "screenshot.jpg"), type="jpeg", quality=70)
    info(f"{kb(len(shot))} saved to {OUT}/screenshot.jpg")
    trace.show()

    step("Get the HTML and turn it into markdown (what the model will read)")
    html = page.content()
    md = to_markdown(html)
    with open(os.path.join(OUT, "page.html"), "w", encoding="utf-8") as f:
        f.write(html)
    with open(os.path.join(OUT, "page.md"), "w", encoding="utf-8") as f:
        f.write(md)
    info(f"HTML {kb(len(html))} -> markdown {kb(len(md))}, about {len(md) // 4} tokens")
    trace.show()

    step("List what can be clicked (so the model can say 'click 7')")
    links = get_links(page)
    with open(os.path.join(OUT, "links.txt"), "w", encoding="utf-8") as f:
        f.write(format_links(links) + "\n")
    info(f"{len(links)} links and buttons, first few:")
    for line in format_links(links[:5]).splitlines():
        info(line)
    trace.show()

    step("Which IP did the website see? (new tab, same session, same proxy)")
    ip_page = page.context.new_page()
    try:
        ip_page.goto("https://ipinfo.io/json", timeout=15000)
        ip = json.loads(ip_page.inner_text("body"))
        info(f"{ip.get('ip')}, {ip.get('city')}, {ip.get('country')}, network: {ip.get('org')}")
        info("hosting company (M247, OVH, ...) = datacenter proxy. Home ISP (Comcast, Vodafone, ...) = residential.")
    except Exception as e:
        info(f"could not check: {e}")
    trace.show(max_lines=4)

    step("Close the session (Browser.close over CDP, not just disconnect)")

trace.show()
info("session closed. Billing stopped.")

print(f"\n{BOLD}Done in {time.time() - t0:.1f}s.{RESET} Look at:")
for name in ["screenshot.jpg", "page.md", "links.txt", "page.html", "cdp_trace.log"]:
    print(f"  {OUT}/{name}")
