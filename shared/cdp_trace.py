"""Show the raw CDP messages Playwright exchanges with the Zyte browser.

Playwright writes every CDP message to a log file when DEBUG=pw:protocol is
set. start() must run before the browser connects. After each step, call
show() to print the messages that step produced, shortened to one line each.
The full log stays in the file.
"""

import json
import os
import re

LINE = re.compile(r"pw:protocol (SEND ►|◀ RECV) (\{.*\})\s*$")

# Events worth printing. Everything else is counted, not shown.
EVENTS = {
    "Target.attachedToTarget",
    "Page.frameNavigated",
    "Page.domContentEventFired",
    "Page.loadEventFired",
    "Network.requestWillBeSent",
    "Network.responseReceived",
    "Network.loadingFailed",
}

# Playwright does most page work by running its own JS in the page.
# The params are long and not interesting, so we only name them.
PLAYWRIGHT_JS = {"Runtime.evaluate", "Runtime.callFunctionOn", "Runtime.releaseObject"}

GREY = "\033[90m"
CYAN = "\033[36m"
RESET = "\033[0m"


def start(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").close()
    os.environ["DEBUG"] = "pw:protocol"
    os.environ["DEBUG_FILE"] = path
    return Trace(path)


class Trace:
    def __init__(self, path):
        self.path = path
        self.offset = 0
        self.methods = {}  # message id -> method, to label responses

    def read_new(self):
        with open(self.path, encoding="utf-8") as f:
            f.seek(self.offset)
            lines = f.readlines()
            self.offset = f.tell()
        for line in lines:
            m = LINE.search(line)
            if m:
                yield m.group(1), json.loads(m.group(2))

    def show(self, max_lines=12):
        shown, hidden = [], 0
        for direction, msg in self.read_new():
            text = self.describe(direction, msg)
            if not text:
                hidden += 1
            elif shown and shown[-1][0] == text:
                shown[-1][1] += 1
            else:
                shown.append([text, 1])
        shown = [t if n == 1 else f"{t} x{n}" for t, n in shown]
        for text in shown[:max_lines]:
            print(f"      {text}")
        rest = len(shown) - max_lines
        if rest > 0 or hidden:
            more = f"{rest} more, " if rest > 0 else ""
            print(f"      {GREY}... {more}{hidden} other messages (network data, lifecycle) in {self.path}{RESET}")

    def describe(self, direction, msg):
        if direction == "SEND ►":
            self.methods[msg["id"]] = msg["method"]
            if msg["method"] in PLAYWRIGHT_JS:
                return f"{CYAN}► {msg['method']}{RESET} {GREY}(JavaScript Playwright runs inside the page){RESET}"
            params = short(msg.get("params"))
            return f"{CYAN}► {msg['method']}{RESET} {params}".rstrip()

        if "id" in msg:  # reply to a command we sent
            method = self.methods.get(msg["id"], "?")
            result = msg.get("result", {})
            if method == "Browser.getVersion":
                return f"◀ {method} {result.get('product')}, user agent: {result.get('userAgent')}"
            if method == "Page.captureScreenshot":
                size = len(result.get("data", "")) * 3 // 4 // 1024
                return f"◀ {method} {size} KB jpeg, sent back as base64"
            if method in ("Page.navigate", "Browser.close"):
                return f"◀ {method} ok {short(result)}".rstrip()
            return None

        method = msg.get("method")
        if method not in EVENTS:
            return None
        p = msg.get("params", {})
        if method == "Network.requestWillBeSent":
            return f"◀ {method} {p['request']['method']} {p['request']['url'][:90]}"
        if method == "Network.responseReceived":
            r = p["response"]
            return f"◀ {method} {r['status']} {r['url'][:90]}"
        if method == "Network.loadingFailed":
            return f"◀ {method} {p.get('errorText')}"
        if method == "Page.frameNavigated":
            return f"◀ {method} {p['frame']['url'][:90]}"
        if method == "Target.attachedToTarget":
            return f"◀ {method} {p['targetInfo']['type']} {p['targetInfo']['url']}"
        return f"◀ {method}"


def short(obj, limit=90):
    if not obj:
        return ""
    text = json.dumps(obj, separators=(",", ":"))
    return text if len(text) <= limit else text[:limit] + "..."
