"""Setup check: open a Zyte browser, show the IP it browses from, close it.

    python lessons/00-setup/check.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.zyte_cdp import zyte_page  # noqa: E402

start = time.time()
with zyte_page(ttl=60) as page:
    print(f"connected in {time.time() - start:.1f}s")
    page.goto("https://httpbin.org/ip")
    print("browsing from:", page.inner_text("body").strip())
print("session closed. You're ready.")

if not os.environ.get("OPENROUTER_API_KEY"):
    print("note: OPENROUTER_API_KEY is not set yet, you need it from lesson 03.")
