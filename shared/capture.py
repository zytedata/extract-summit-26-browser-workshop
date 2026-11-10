"""Turn the current page into what the agent works with.

- screenshot: what the model looks at
- markdown: the page text without scripts, styles and markup noise
- links: numbered list of what can be clicked, so the model can say "click 7"
- snapshot: Playwright's accessibility tree (page.aria_snapshot(mode="ai")),
  trimmed. Roles, names, states and refs: the model says "e61", our code does
  page.get_by_ref("e61").click(). See research/ for when to send which.
"""

import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from markdownify import markdownify

NOISE = ["script", "style", "noscript", "svg", "iframe", "template"]

# Runs inside the browser. Visible links and buttons only. Each one we keep
# gets a data-agent-n attribute with its number, so "click 7" can find it
# again later with the selector [data-agent-n="7"].
LINKS_JS = """
() => {
  document.querySelectorAll('[data-agent-n]').forEach(el => el.removeAttribute('data-agent-n'));
  const seen = new Set();
  const out = [];
  for (const el of document.querySelectorAll('a[href], button, [role=button], [role=tab], [role=switch]')) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    const text = (el.innerText || el.getAttribute('aria-label') || '').trim().replace(/\\s+/g, ' ').slice(0, 80);
    const href = el.tagName === 'A' ? el.href : '';
    const key = text + '|' + href;
    if (!text || seen.has(key)) continue;
    seen.add(key);
    out.push({tag: el.tagName.toLowerCase(), text, href});
    el.setAttribute('data-agent-n', out.length);
  }
  return out;
}
"""


def to_markdown(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(NOISE):
        tag.decompose()
    md = markdownify(str(soup), heading_style="ATX")
    return re.sub(r"\n{3,}", "\n\n", md).strip()


def get_links(page):
    return page.evaluate(LINKS_JS)


def format_links(links):
    lines = []
    for i, link in enumerate(links, 1):
        target = f" -> {link['href']}" if link["href"] else f" [{link['tag']}]"
        lines.append(f"{i:>3}. {link['text']}{target}")
    return "\n".join(lines)


# An unnamed div: "- generic [ref=e5]:". Its children stay, one level up.
_WRAPPER = re.compile(r"^- generic(?: \[[^\]]*\])*:?$")
_TAGS = re.compile(r" \[cursor=pointer\]| \[active\]")


def snapshot(page, url=None):
    """The page's aria snapshot, trimmed for a model (about 30-45% smaller, same tree)."""
    return compact_snapshot(page.aria_snapshot(mode="ai"), url or page.url)


def compact_snapshot(text, base_url=""):
    host = urlparse(base_url).netloc
    out, dropped = [], []  # indents of removed wrappers that are still open
    for line in text.splitlines():
        indent = len(line) - len(line.lstrip(" "))
        body = line.strip()
        while dropped and indent <= dropped[-1]:
            dropped.pop()
        if _WRAPPER.match(body) or body in ("- img", "- separator"):
            if body.endswith(":"):
                dropped.append(indent)
            continue
        body = _TAGS.sub("", body)
        if body.startswith("- /url:"):
            u = urlparse(body[len("- /url:"):].strip().strip('"'))
            body = "- /url: " + ((u.path or "/") if u.netloc in ("", host) else u.netloc + u.path)
        body = re.sub(r"^- generic (\[ref=\w+\]): ", r"- \1 ", body)  # "- generic [ref=e40]: text" -> "- [ref=e40] text"
        out.append(" " * (indent - 2 * len(dropped)) + body)
    return "\n".join(out)
