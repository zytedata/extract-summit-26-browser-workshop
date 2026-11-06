"""The competitor list from lesson 02."""

import json
import os

PATH = os.path.join(os.path.dirname(__file__), "..", "data", "web-scraping.json")


def pick_url(target):
    """A company name from data/web-scraping.json, or a URL as is."""
    if target.startswith("http"):
        return target
    with open(PATH, encoding="utf-8") as f:
        companies = json.load(f)["companies"]
    for c in companies:
        if c["name"].lower() == target.lower():
            return c["homepage"]
    names = ", ".join(c["name"] for c in companies)
    raise SystemExit(f"{target!r} is not in data/web-scraping.json. Pick one of: {names}. Or pass a URL.")
