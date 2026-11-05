"""Open a Zyte browser over CDP and make sure the session ends.

Playwright's browser.close() only disconnects. The Zyte session keeps running
(and billing) until ttl. So we send Browser.close over CDP when we're done.
ttl is the safety net if the script crashes.
"""

import base64
import os
from contextlib import contextmanager

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

CDP_ENDPOINT = "https://browser.zyte.com/"


def auth_headers():
    key = os.environ.get("ZYTE_API_KEY")
    if not key:
        raise SystemExit("ZYTE_API_KEY is not set. Copy .env.example to .env and add your key.")
    token = base64.b64encode(f"{key}:".encode()).decode()
    return {"Authorization": f"Basic {token}"}


@contextmanager
def zyte_page(ttl=120):
    """Yield a Playwright page running in a Zyte browser."""
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"{CDP_ENDPOINT}?ttl={ttl}", headers=auth_headers())
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()
        try:
            yield page
        finally:
            try:
                page.context.new_cdp_session(page).send("Browser.close")
            except Exception:
                pass  # already gone, ttl will clean up
