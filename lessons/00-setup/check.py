"""Setup check: open a Zyte browser, see where websites think it is, close it.

    python lessons/00-setup/check.py

It asks ipinfo.io twice: once from your laptop, once from the Zyte browser.
Two different places means your traffic goes through Zyte. Only the city and
country are printed, no IP addresses.
"""

import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.zyte_cdp import where, zyte_page  # noqa: E402


def laptop():
    try:
        with urllib.request.urlopen("https://ipinfo.io/json", timeout=5) as r:
            return where(json.load(r))
    except Exception:
        return "unknown (couldn't check)"


print(f"your laptop:      {laptop()}")
start = time.time()
with zyte_page(ttl=60) as page:
    print(f"connected in {time.time() - start:.1f}s")
    page.goto("https://ipinfo.io/json")
    print(f"the Zyte browser: {where(json.loads(page.inner_text('body')))}")
print("session closed. You're ready.")

if not os.environ.get("OPENROUTER_API_KEY"):
    print("note: OPENROUTER_API_KEY is not set yet, you need it from lesson 03.")
