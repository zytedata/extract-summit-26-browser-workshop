"""Open a Zyte browser over CDP and make sure the session ends.

Playwright's browser.close() only disconnects. The Zyte session keeps running
(and billing) until ttl. So we send Browser.close over CDP when we're done.
ttl is the safety net if the script crashes.

With trace="path/trace.zip" the whole session is recorded with Playwright
tracing: a filmstrip, the page (DOM) before and after every action, network
and console. Replay it with `playwright show-trace path/trace.zip`, or drop
the file on https://trace.playwright.dev (it stays in your browser).
"""

import base64
import os
import time
from contextlib import contextmanager

from dotenv import find_dotenv, load_dotenv
from playwright.sync_api import sync_playwright

# Found from the repo, wherever you run the script from. .env.local wins if both exist.
load_dotenv(find_dotenv(".env.local"))
load_dotenv(find_dotenv(".env"))

CDP_ENDPOINT = "https://browser.zyte.com/"


def auth_headers():
    key = os.environ.get("ZYTE_API_KEY")
    if not key:
        raise SystemExit("ZYTE_API_KEY is not set. Copy .env.example to .env and add your key.")
    token = base64.b64encode(f"{key}:".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def connect_url(ttl=120, proxy_type=None, proxy_region=None):
    """proxy_type (datacenter/residential) and proxy_region (country code) are
    optional. Left out, Zyte picks what works best for the first site you open."""
    url = f"{CDP_ENDPOINT}?ttl={ttl}"
    if proxy_type:
        url += f"&proxy_type={proxy_type}"
    if proxy_region:
        url += f"&proxy_region={proxy_region}"
    return url


def connect(p, url, attempts=4):
    """429 means your account has as many browsers open as it's allowed.
    Wait for one to finish and try again."""
    for attempt in range(1, attempts + 1):
        try:
            return p.chromium.connect_over_cdp(url, headers=auth_headers())
        except Exception as e:
            if "429" not in str(e) or attempt == attempts:
                raise
            wait = 5 * attempt
            print(f"browser limit reached (429), trying again in {wait}s")
            time.sleep(wait)


@contextmanager
def zyte_page(ttl=120, proxy_type=None, proxy_region=None, trace=None):
    """Yield a Playwright page running in a Zyte browser."""
    with sync_playwright() as p:
        url = connect_url(ttl, proxy_type, proxy_region)
        browser = connect(p, url)
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        if trace:
            context.tracing.start(screenshots=True, snapshots=True)
        page = context.new_page()
        try:
            yield page
        finally:
            if trace:  # save it before closing, also when the script crashed
                try:
                    os.makedirs(os.path.dirname(trace) or ".", exist_ok=True)
                    context.tracing.stop(path=trace)
                except Exception as e:
                    print(f"could not save the trace: {e}")
            try:
                page.context.new_cdp_session(page).send("Browser.close")
            except Exception:
                pass  # already gone, ttl will clean up


@contextmanager
def trace_step(page, title):
    """Group what happens inside under one title in the trace viewer.
    Does nothing visible when the session isn't traced."""
    page.context.tracing.group(title)
    try:
        yield
    finally:
        page.context.tracing.group_end()


def settle(page, timeout=10_000):
    """Wait for the "load" event, but not forever. Some pages keep one request
    open (a tracker, a chat widget) and "load" never fires. The page is usable
    long before that, so after `timeout` we just carry on."""
    try:
        page.wait_for_load_state("load", timeout=timeout)
        return True
    except Exception:
        return False


def open_url(page, url):
    """page.goto that doesn't hang on pages that never finish loading."""
    response = page.goto(url, wait_until="domcontentloaded", timeout=30_000)
    settle(page)
    return response
