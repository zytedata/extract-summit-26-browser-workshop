# Build a browser agent on Zyte CDP

Extract Summit 2026, Dublin. Hands-on workshop, 90 min.

You get a question from your boss: "who are our competitors and what do they charge?". In this workshop you build a small agent that answers it. It drives a real browser (Zyte Browser over CDP), looks at each page, describes what it sees and decides where to click next. Then you run it on a list of competitors and turn what it found into a pricing table.

About 100 lines of Python you can read end to end and take home.

## Lessons

| # | Lesson | What you do | Time |
|---|---|---|---|
| 00 | [Setup](lessons/00-setup/) | Check you can open a Zyte browser | 10 min |
| 01 | [First session](lessons/01-first-session/) | How it works, then one session step by step with the CDP trace | 10 min |
| 02 | [Find the competitors](lessons/02-find-competitors/) | Where the competitor list comes from: search, list articles, no browser | 5 min |
| 03 | [Describe a page](lessons/03-describe-a-page/) | Send a page to a model, get back what it is, prices, where pricing is | 15 min |
| 04 | [Agent loop](lessons/04-agent-loop/) | Let the model pick the next click, loop until it finds pricing | 20 min |
| 05 | [Explore competitors](lessons/05-explore-competitors/) | Run your agent on the competitor list, a few sessions in parallel | 15 min |
| 06 | [Report](lessons/06-report/) | Turn the captured pages into a pricing comparison | 10 min |

No coding needed. Each lesson has a README and a script you run: it explains a step, you run it, you look at the output. Read the scripts if you want to see how it's done, they're short.

## Setup

Do this before the workshop if you can. Conference wifi is not your friend.

### 1. What you need

- Python 3.10 or newer (3.12 recommended, that's what the workshop is tested on)
- git
- A Zyte account with an API key: https://app.zyte.com
- An OpenRouter API key: https://openrouter.ai/keys. One key for many models (Claude, Gemini, GPT, ...)

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

Open `.env` and fill in `ZYTE_API_KEY` and `OPENROUTER_API_KEY`. `OPENROUTER_MODEL` is optional, the default is `anthropic/claude-haiku-5.5`. Any model that reads images works.

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
data/                  the competitor list from lesson 02, saved so every run starts the same
output/                what your agent captures (git ignored)
```

## A note on cost

A Zyte browser session costs whichever is higher: the number of pages you open, or its length in 15 second blocks. A session left open keeps counting until its `ttl`, so the helper in `shared/` always ends it when your script finishes, even if it crashes. Model calls are billed per token by OpenRouter, the scripts print the cost of each call. A full run of the workshop should cost a few dollars at most.

## Contributing

This repo runs a secrets scan on every push. Before you commit:

```bash
pip install detect-secrets pre-commit
pre-commit install
pre-commit run --all-files
```

## License

Apache 2.0, see [LICENSE](LICENSE).
