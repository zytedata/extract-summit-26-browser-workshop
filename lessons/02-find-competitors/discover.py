"""Find companies in a space from "best X companies" list articles. No browser.

    python lessons/02-find-competitors/discover.py "web scraping"
    python lessons/02-find-competitors/discover.py "specialty coffee roasters" --articles 8

1. Search Bing for list articles ("best web scraping companies", ...)
2. Pull the article body from each one with Zyte API article extraction
3. Company names come from the numbered headings ("3. Apify"), that's how
   list articles are written. Count in how many articles each name shows up.
   More mentions = more likely a real player.
4. Homepage: the article's own link if it has one, otherwise a Bing lookup
   for "<name> official site".

Output: output/02/<query-slug>.json. The later lessons read the saved copy in
data/web-scraping.json instead, because search results change from run to run.
--save writes there (that's how the saved copy was made).
"""

import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from urllib.parse import parse_qs, quote_plus, urljoin, urlparse

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.zyte_cdp import auth_headers  # noqa: E402

REPO = os.path.join(os.path.dirname(__file__), "..", "..")

QUERIES = [
    "best {q} companies",
    "top {q} companies",
    "best {q} services",
    "top {q} providers",
    "{q} companies list",
    "{q} providers compared",
]

# Links in articles that are never the companies we're after
SKIP_DOMAINS = {
    "twitter.com", "x.com", "facebook.com", "linkedin.com", "instagram.com",
    "youtube.com", "youtu.be", "tiktok.com", "pinterest.com", "reddit.com",
    "wikipedia.org", "google.com", "bing.com", "apple.com", "amazon.com",
    "github.com", "medium.com", "bit.ly", "t.co", "g2.com", "capterra.com",
    "trustpilot.com", "gartner.com", "producthunt.com", "w3.org",
    # ad and affiliate redirects that list articles link through
    "googleadservices.com", "doubleclick.net", "technologyadvice.com",
}

# Fewer numbered entries than this and it's not a list article
MIN_ENTRIES = 4

# "3. Apify", "#3 Apify", "3) Apify - the scraping platform"
NUMBERED = re.compile(r"^\s*(?:#\d{1,2}[.):-]?|\d{1,2}\s*[.):-])\s*(.+)$")


def zyte(payload):
    req = urllib.request.Request(
        "https://api.zyte.com/v1/extract",
        data=json.dumps(payload).encode(),
        headers={**auth_headers(), "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.load(resp)


def domain(url):
    """https://blog.example.co.uk/x -> example.co.uk"""
    host = urlparse(url).netloc.lower().split(":")[0].removeprefix("www.")
    parts = host.split(".")
    if len(parts) > 2 and parts[-2] in ("co", "com", "org", "net", "ac") and len(parts[-1]) == 2:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


# Search

def real_url(href):
    """Bing wraps results in bing.com/ck/a?...&u=a1<base64 of the real url>."""
    if "bing.com/ck/a" not in href:
        return href
    u = parse_qs(urlparse(href).query).get("u", [""])[0]
    if not u.startswith("a1"):
        return href
    b64 = u[2:]
    return base64.urlsafe_b64decode(b64 + "=" * (-len(b64) % 4)).decode()


# Words that say nothing about the topic, so they don't count when we check
# whether Bing answered the question we asked.
FILLER = {"best", "top", "companies", "services", "providers", "list", "compared", "official", "site"}


def search(query, attempts=4):
    """Bing results for query: [{title, url, snippet}].

    Now and then Bing answers with results for something else entirely (in
    November 2026: a shop called BESTSECRET and restaurants in Dacula, GA),
    even though the page shows our query in the search box. It comes and goes,
    from 1 in 10 requests to 9 in 10. So check that the results are about the
    query, and ask again if they aren't. Each try goes out through a new proxy.
    Still off topic after every try: no results, rather than junk.
    """
    topic = [w for w in query.lower().split() if w not in FILLER]
    for _ in range(attempts):
        results = _bing(query)
        on_topic = [r for r in results if any(w in (r["title"] + " " + r["url"]).lower() for w in topic)]
        if results and len(on_topic) >= len(results) / 2:
            return results
    return []


def _bing(query):
    url = f"https://www.bing.com/search?q={quote_plus(query)}&setlang=en&cc=US"
    html = base64.b64decode(zyte({"url": url, "httpResponseBody": True})["httpResponseBody"]).decode("utf-8", "replace")
    soup = BeautifulSoup(html, "html.parser")
    results = []
    # Organic results go through bing.com/ck/a, ads through bing.com/aclk.
    # Bing's markup nests badly for html.parser, so start from the headings.
    for a in soup.select('h2 a[href*="bing.com/ck/a"]'):
        li = a.find_parent("li") or a.parent
        snippet = li.select_one(".b_caption p, .b_lineclamp2, .b_lineclamp3, .b_lineclamp4")
        results.append({
            "title": a.get_text(" ", strip=True),
            "url": real_url(a["href"]),
            "snippet": snippet.get_text(" ", strip=True) if snippet else "",
        })
    return results


# Articles

def clean_name(text):
    """'Bright Data - best for scale' -> 'Bright Data'"""
    name = re.split(r"\s+[-\u2013\u2014|:(]\s*|:\s", text, maxsplit=1)[0]
    return name.strip(" .*") if 1 < len(name) <= 40 else None


def key(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def read_article(url):
    try:
        data = zyte({"url": url, "article": True, "articleOptions": {"extractFrom": "httpResponseBody"}})
    except urllib.error.HTTPError as e:
        return {"url": url, "error": f"HTTP {e.code}", "entries": []}
    art = data.get("article") or {}
    soup = BeautifulSoup(art.get("articleBodyHtml") or "", "html.parser")
    own = domain(url)

    # Outbound links, to match against names later
    links = {}
    for a in soup.select("a[href]"):
        href = urljoin(url, a["href"])
        d = domain(href)
        if href.startswith("http") and d != own and d not in SKIP_DOMAINS:
            links.setdefault(key(a.get_text()), d)
            links.setdefault(key(d.split(".")[0]), d)

    entries = []
    for h in soup.select("h2, h3, h4"):
        m = NUMBERED.match(h.get_text(" ", strip=True))
        name = m and clean_name(m.group(1))
        if name and key(name) not in {key(e["name"]) for e in entries}:
            k = key(name)
            entries.append({"name": name, "domain": links.get(k) or name_as_domain(name)})
    return {"url": url, "headline": art.get("headline"), "entries": entries}


def name_as_domain(name):
    """'Webscraper.io' and 'Scrape.do' are their own homepage."""
    return name.lower() if re.fullmatch(r"[a-z0-9-]+\.[a-z]{2,6}", name.lower()) else None


def looks_like(name, d):
    """Does the domain belong to the company? 'Browse AI' ~ browse.ai, 'Bright Data' ~ brightdata.com"""
    label, k = key(d.split(".")[0]), key(name)
    return label.startswith(k[:5]) or k.startswith(label[:5]) or key(d).startswith(k)


def find_homepage(name):
    # Bing over plain HTTP sometimes answers a different question, so only
    # accept a result whose domain looks like the company name.
    for r in search(f"{name} official site"):
        d = domain(r["url"])
        if d not in SKIP_DOMAINS and looks_like(name, d):
            return d
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help='what the companies do, e.g. "web scraping"')
    parser.add_argument("--articles", type=int, default=6, help="how many list articles to read")
    parser.add_argument("--save", action="store_true", help="write to data/ instead of output/02/")
    args = parser.parse_args()

    print(f"Searching Bing for list articles about {args.query!r}")
    seen, candidates = set(), []
    for template in QUERIES:
        q = template.format(q=args.query)
        results = search(q)
        print(f"  {q!r}: {len(results)} results")
        for r in results:
            if r["url"].startswith("http") and r["url"] not in seen and domain(r["url"]) not in SKIP_DOMAINS:
                seen.add(r["url"])
                candidates.append({**r, "query": q})

    # Read more than we need: some won't be list articles
    to_read = candidates[: args.articles * 3]
    print(f"\nReading {len(to_read)} articles with Zyte API article extraction")
    with ThreadPoolExecutor(max_workers=6) as pool:
        read = list(pool.map(read_article, [c["url"] for c in to_read]))

    articles = []
    for cand, art in zip(to_read, read):
        n = len(art["entries"])
        status = art.get("error") or f"{n} companies"
        ok = n >= MIN_ENTRIES and len(articles) < args.articles
        print(f"  {'+' if ok else '-'} {status:>12}  {cand['url']}")
        if ok:
            articles.append({**cand, "headline": art["headline"], "entries": art["entries"]})

    companies = {}
    for art in articles:
        for e in art["entries"]:
            c = companies.setdefault(key(e["name"]), {"name": e["name"], "domain": None, "articles": []})
            c["domain"] = c["domain"] or e["domain"]
            if art["url"] not in c["articles"]:
                c["articles"].append(art["url"])

    missing = [c for c in companies.values() if not c["domain"]]
    print(f"\n{len(companies)} companies, looking up {len(missing)} homepages on Bing")
    with ThreadPoolExecutor(max_workers=6) as pool:
        for c, d in zip(missing, pool.map(lambda c: find_homepage(c["name"]), missing)):
            c["domain"] = d

    ranked = sorted(companies.values(), key=lambda c: (-len(c["articles"]), c["name"].lower()))
    out = {
        "query": args.query,
        "fetched": date.today().isoformat(),
        "searches": [t.format(q=args.query) for t in QUERIES],
        "articles": [
            {k: a[k] for k in ("title", "url", "query", "snippet")} | {"companies": [e["name"] for e in a["entries"]]}
            for a in articles
        ],
        "companies": [
            {
                "name": c["name"],
                "homepage": f"https://{c['domain']}/" if c["domain"] else None,
                "mentions": len(c["articles"]),
                "found_in": c["articles"],
            }
            for c in ranked
        ],
    }

    slug = re.sub(r"[^a-z0-9]+", "-", args.query.lower()).strip("-")
    folder = os.path.join(REPO, "data" if args.save else os.path.join("output", "02"))
    os.makedirs(folder, exist_ok=True)
    path = os.path.normpath(os.path.join(folder, f"{slug}.json"))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\n{len(ranked)} companies from {len(articles)} articles. Top 20:")
    for c in out["companies"][:20]:
        print(f"  {c['mentions']}x  {c['name']:<28} {c['homepage'] or '?'}")
    print(f"\nSaved to {path}")


if __name__ == "__main__":
    main()
