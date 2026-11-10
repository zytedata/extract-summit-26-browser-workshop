"""What should the model see? Screenshot, markdown + links, or the accessibility snapshot.

    python research/what_to_send.py                 # 5 pages x 5 setups x 2 runs, ~5 units, ~$0.10
    python research/what_to_send.py --runs 1 --model google/gemini-3.5-flash-lite

One Zyte session per page captures everything (each capture timed twice), then
the same question goes to the model five ways. Results and what was captured
land in output/research/. Grading which answers are right is done by hand,
see research/README.md for the 2026-11-10 run.
"""
import argparse, json, os, statistics, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared import llm
from shared.capture import compact_snapshot, format_links, get_links, to_markdown
from shared.zyte_cdp import open_url, zyte_page

ap = argparse.ArgumentParser()
ap.add_argument("--runs", type=int, default=2)
ap.add_argument("--model")
args = ap.parse_args()
OUT = os.path.join("output", "research"); os.makedirs(OUT, exist_ok=True)
PAGES = ['https://apify.com/pricing', 'https://www.zyte.com/', 'https://www.octoparse.com/pricing',
         'https://brightdata.com/pricing/web-unlocker', 'https://oxylabs.io/']
SYSTEM = """You look at one web page of a company. Answer with JSON only, in the shape you were given.
Use only what is on the page.
prices: every plan price visible now, with its billing period and what the plan includes. Empty if none.
target: the one element to click next to get the full pricing. On a page that isn't pricing: the way to the
pricing page. On a pricing page with a monthly/annual toggle: the toggle option that isn't selected yet.
If a cookie banner or popup hides the content: the button that closes it. Empty string if there's nothing to click."""
HOW = {
    'links': 'Give target as the number of the link or button from the numbered list.',
    'ref': 'Give target as the ref of the element from the snapshot, like e123.',
    'text': 'Give target as the exact visible text of the element in the screenshot.',
}
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["page_type", "prices", "why", "target"],
  "properties": {"page_type": {"type": "string", "enum": ["home", "pricing", "product", "other"]},
    "prices": {"type": "array", "items": {"type": "object", "additionalProperties": False,
       "required": ["plan", "amount", "period", "includes"],
       "properties": {"plan": {"type": "string"}, "amount": {"type": "string"}, "period": {"type": "string"},
                      "includes": {"type": "array", "items": {"type": "string"}}}}},
    "why": {"type": "string"}, "target": {"type": "string"}}}

def timed(f, n=2):
    ts, val = [], None
    for _ in range(n):
        t = time.time(); val = f(); ts.append(time.time() - t)
    return val, round(statistics.median(ts), 2)

rows = []
for url in PAGES:
    site = url.split('/')[2].removeprefix('www.')
    with zyte_page(ttl=180) as page:
        open_url(page, url)
        page.wait_for_timeout(1500)
        shot, t_shot = timed(lambda: page.screenshot(type='jpeg', quality=70))
        (md, links), t_md = timed(lambda: (to_markdown(page.content()), get_links(page)))
        raw, t_aria = timed(lambda: page.aria_snapshot(mode='ai'))
    aria = compact_snapshot(raw, url)
    open(f'{OUT}/{site}.shot.jpg', 'wb').write(shot)
    open(f'{OUT}/{site}.md', 'w').write(md); open(f'{OUT}/{site}.aria.yaml', 'w').write(aria)
    open(f'{OUT}/{site}.links.txt', 'w').write(format_links(links))
    mdp = llm.text_part(f"URL: {url}\n\n# Page text (markdown)\n\n{md[:30000]}")
    lkp = llm.text_part(f"# Links and buttons\n\n{format_links(links[:150])}")
    arp = llm.text_part(f"URL: {url}\n\n# Page (accessibility snapshot)\n\n{aria[:60000]}")
    img = llm.image_part(shot)
    setups = {
        'A screenshot+markdown+links': ([img, mdp, lkp], 'links', t_shot + t_md),
        'B snapshot':                  ([arp], 'ref', t_aria),
        'C snapshot+screenshot':       ([img, arp], 'ref', t_aria + t_shot),
        'D markdown+links':            ([mdp, lkp], 'links', t_md),
        'E screenshot':                ([llm.text_part(f"URL: {url}"), img], 'text', t_shot),
    }
    cap = dict(site=site, shot_kb=len(shot) // 1024, md_chars=len(md), md_sent=min(len(md), 30000), links=len(links),
               aria_raw=len(raw), aria=len(aria), t_shot=t_shot, t_md_links=t_md, t_aria=t_aria)
    print('##', json.dumps(cap), flush=True)
    for name, (parts, how, t_cap) in setups.items():
        for run in range(1, args.runs + 1):
            try:
                ans, st = llm.ask(SYSTEM + '\n' + HOW[how], parts, SCHEMA, model=args.model)
            except SystemExit as e:
                print('FAIL', site, name, e, flush=True); continue
            tgt = ans['target'].strip()
            if how == 'links' and tgt.isdigit() and 1 <= int(tgt) <= len(links):
                shown = links[int(tgt) - 1]['text']
            elif how == 'ref':
                shown = next((l.strip() for l in aria.splitlines() if f'[ref={tgt}]' in l), '(ref not found)')
            else:
                shown = tgt
            r = dict(cap, setup=name, run=run, capture_s=round(t_cap, 2), model_s=st['seconds'], tok_in=st['input_tokens'],
                     tok_out=st['output_tokens'], usd=st['cost_usd'], page_type=ans['page_type'],
                     prices=[f"{p['plan']}: {p['amount']} / {p['period']}" for p in ans['prices']],
                     includes=[len(p['includes']) for p in ans['prices']], target=tgt, target_is=shown[:100], why=ans['why'])
            rows.append(r)
            print(json.dumps({k: r[k] for k in ('site', 'setup', 'run', 'tok_in', 'usd', 'model_s', 'target', 'target_is')} | {'n_prices': len(r['prices'])}, ensure_ascii=False), flush=True)
            json.dump(rows, open(f'{OUT}/results.json', 'w'), indent=1, ensure_ascii=False)
