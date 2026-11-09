# Give Claude a Chrome that doesn't get blocked

Extract Summit 2026, Dublin. Hands-on workshop, 90 min.

You are building a startup and you need to find out "who are our competitors and what do they charge?". In this workshop you answer it with a small browser agent: Claude, the model, called through an API, does the looking and deciding, and a real Chrome in Zyte's cloud does the browsing, without getting blocked. Any model that reads images works, Claude is the default. First you find the competitors from "best X companies" articles. Then the agent drives a real browser (Zyte Browser over CDP) on each competitor's site: it looks at the page, says what it sees, and decides where to click next until it has the prices. At the end you turn what it found into a pricing table.

You don't write the agent, you run it step by step and look at what happens at each step. The code is plain Python with no framework, short enough to read end to end and take home.

## Lessons

| # | Lesson | What you do | Time |
|---|---|---|---|
| 00 | [Setup](lessons/00-setup/) | Check you can open a Zyte browser | 10 min |
| 01 | [First session](lessons/01-first-session/) | How it works, then one session step by step with the CDP trace | 10 min |
| 02 | [Find the competitors](lessons/02-find-competitors/) | Where the competitor list comes from: search, list articles, no browser | 5 min |
| 03 | [Describe a page](lessons/03-describe-a-page/) | Send a page to a model, get back what it is, prices, where pricing is | 15 min |
| 04 | [Agent loop](lessons/04-agent-loop/) | Let the model pick the next click, loop until it finds pricing | 20 min |
| 05 | [Explore competitors](lessons/05-explore-competitors/) | Run the agent on 5 competitors, 3 at a time, and watch them in a live dashboard | 15 min |
| 06 | [Report](lessons/06-report/) | Read the dashboard: entry prices, plan ladders, annual discounts, what it cost | 10 min |

No coding needed. Each lesson has a README and a script you run: it explains a step, you run it, you look at the output. Read the scripts if you want to see how it's done, they're short.

Wifi gone? Lessons 05 and 06 work offline from a recorded run: `python lessons/05-explore-competitors/explore.py --replay`.

## Setup

Do this before the workshop if you can. Conference wifi is not your friend.

### 1. What you need

- Python 3.10 or newer (3.12 recommended, that's what the workshop is tested on)
- git
- A Zyte account with an API key: https://app.zyte.com
- An OpenRouter API key: https://openrouter.ai/keys. One key for many models (Claude, Gemini, GPT, ...)

You don't need to install a browser to run the lessons. The browser runs on Zyte's side, your script just connects to it.

### 2. Unlock the browser on your Zyte account

The Zyte browser needs a verified business account. Two things, both in https://app.zyte.com:

1. **A paid plan.** Pay as you go, or a subscription. Pay as you go is enough for the workshop: you only pay for what you use, and a full run of every lesson costs a few dollars at most.
2. **A short form about your business.** Company name, what you'll use the browser for, that kind of thing. It's reviewed by Zyte, so don't leave it for the morning of the workshop.

Once the review is done, Browser CDP works with your normal Zyte API key. Step 6 below checks it.

### 3. Get the code

```bash
git clone https://github.com/zytedata/extract-summit-26-browser-workshop.git
cd extract-summit-26-browser-workshop
```

### 4. Install

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

If you use uv: `uv venv && uv pip install -r requirements.txt`.

### 5. Add your keys

```bash
cp .env.example .env
```

Open `.env` and fill in `ZYTE_API_KEY` and `OPENROUTER_API_KEY`. `OPENROUTER_MODEL` is optional, the default is `anthropic/claude-haiku-5.5`. Any model that reads images works. A `.env.local` works too, and wins if you have both.

### 6. Check it works

```bash
python lessons/00-setup/check.py
```

You should see something like:

```
connected in 2.1s
browsing from: {
  "origin": "147.53.113.103"
}
session closed. You're ready.
```

The IP is not yours. That's the Zyte browser.

### 7. Trace viewer (optional)

Lessons 03 to 05 record each browser session as a Playwright trace you can replay step by step. Two ways to open one:

- No install: drop the `trace.zip` on https://trace.playwright.dev. The file stays in your browser.
- Locally: `playwright show-trace output/04/apify.com/trace.zip`. This needs a local Chromium for the viewer, so run `playwright install chromium` before the workshop. It's a big download.

### Troubleshooting

- `ZYTE_API_KEY is not set` - the `.env` file is missing or the key line is empty.
- `401` or `403` when connecting - check the key, and that your account has a paid plan and the business form is approved (step 2).
- Hangs on connect - corporate VPN or proxy blocking websockets. Try without the VPN.
- `429` when connecting - you have as many browsers open as your Zyte account allows. Wait for one to finish.
- `OPENROUTER_API_KEY is not set` or `OpenRouter said 401` - the key is missing or wrong in `.env`.
- `OpenRouter said 402` - the OpenRouter key is out of credit.
- `connection problem ..., trying again` - wifi dropped mid request. The scripts try 3 times before giving up.

## Repo layout

```
shared/zyte_cdp.py     opens a Zyte browser, always closes the session, records the trace
shared/capture.py      page -> screenshot, markdown, numbered links and buttons
shared/llm.py          one call to a model through OpenRouter, JSON back, tokens and cost
shared/companies.py    looks up a company in the list from lesson 02
shared/store.py        the SQLite database agents write to and the dashboard reads
shared/cdp_trace.py    the raw CDP messages view in lesson 01
lessons/NN-name/       one folder per lesson
diagrams/              the lesson diagrams, animated: open in a browser, space for the next step
data/                  the competitor list from lesson 02, and a recorded run for --replay
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
