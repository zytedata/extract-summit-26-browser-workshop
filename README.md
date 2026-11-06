# Build a browser agent on Zyte CDP

Extract Summit 2026, Dublin. Hands-on workshop, 90 min.

You get a question from your boss: "who are our competitors and what do they charge?". In this workshop you build a small agent that answers it. It drives a real browser (Zyte Browser over CDP), looks at each page, describes what it sees and decides where to click next. Then you run it on a list of competitors and turn what it found into a pricing table.

About 100 lines of Python you can read end to end and take home.

## Lessons

| # | Lesson | What you do | Time |
|---|---|---|---|
| 00 | [Setup](lessons/00-setup/) | Check you can open a Zyte browser | 10 min |
| 01 | [First session](lessons/01-first-session/) | How it works, then one session step by step with the CDP trace | 10 min |
| 02 | [Describe a page](lessons/02-describe-a-page/) | Send a page to Claude, get back a description and page type | 15 min |
| 03 | [Agent loop](lessons/03-agent-loop/) | Let Claude pick the next click, loop until it finds pricing | 20 min |
| 04 | [Explore competitors](lessons/04-explore-competitors/) | Run your agent on a list of sites, a few sessions in parallel | 15 min |
| 05 | [Report](lessons/05-report/) | Turn the captured pages into a pricing comparison | 10 min |

Each lesson folder has a README, a starter file and a `solution/` folder if you get stuck. Lessons build on each other, but you can start any lesson from the previous solution.

## Setup

Do this before the workshop if you can. Conference wifi is not your friend.

### 1. What you need

- Python 3.10 or newer
- git
- A Zyte account with an API key: https://app.zyte.com
- An Anthropic API key: https://console.anthropic.com

You don't need to install a browser. The browser runs on Zyte's side, your script just connects to it.

### 2. Get the code

```bash
git clone https://github.com/zytedata/extract-summit-26-browser-workshop.git
cd extract-summit-26-browser-workshop
```

### 3. Install

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

If you use uv: `uv venv && uv pip install -r requirements.txt`.

### 4. Add your keys

```bash
cp .env.example .env
```

Open `.env` and fill in `ZYTE_API_KEY` and `ANTHROPIC_API_KEY`.

### 5. Check it works

```bash
python lessons/00-setup/check.py
```

You should see something like:

```
connected in 2.1s
browsing from: {"origin": "147.53.113.103"}
session closed. You're ready.
```

The IP is not yours. That's the Zyte browser.

### Troubleshooting

- `ZYTE_API_KEY is not set` - the `.env` file is missing or the key line is empty.
- `401` or `403` when connecting - check the key, and that Browser CDP is enabled on your Zyte account.
- Hangs on connect - corporate VPN or proxy blocking websockets. Try without the VPN.

## Repo layout

```
shared/zyte_cdp.py     opens a Zyte browser and always closes the session
lessons/NN-name/       one folder per lesson
data/                  companies found from "best X companies" list articles (discover.py, no browser)
output/                what your agent captures (git ignored)
```

## A note on cost

A Zyte browser session costs whichever is higher: the number of pages you open, or its length in 15 second blocks. A session left open keeps counting until its `ttl`, so the helper in `shared/` always ends it when your script finishes, even if it crashes. Claude calls are billed per token. A full run of the workshop should cost a few dollars at most.

## Contributing

This repo runs a secrets scan on every push. Before you commit:

```bash
pip install detect-secrets pre-commit
pre-commit install
pre-commit run --all-files
```

## License

Apache 2.0, see [LICENSE](LICENSE).
