"""Turn the current page into what the agent works with.

- screenshot: what the model looks at
- markdown: the page text without scripts, styles and markup noise
- links: numbered list of what can be clicked, so the model can say "click 7"
"""

import re

from bs4 import BeautifulSoup
from markdownify import markdownify

NOISE = ["script", "style", "noscript", "svg", "iframe", "template"]

# Runs inside the browser. Visible links and buttons only.
LINKS_JS = """
() => {
  const seen = new Set();
  const out = [];
  for (const el of document.querySelectorAll('a[href], button, [role=button]')) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    const text = (el.innerText || el.getAttribute('aria-label') || '').trim().replace(/\\s+/g, ' ').slice(0, 80);
    const href = el.tagName === 'A' ? el.href : '';
    const key = text + '|' + href;
    if (!text || seen.has(key)) continue;
    seen.add(key);
    out.push({tag: el.tagName.toLowerCase(), text, href});
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
